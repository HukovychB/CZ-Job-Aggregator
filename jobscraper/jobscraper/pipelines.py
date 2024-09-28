# ITEM PIPELINES

from itemadapter import ItemAdapter
from deep_translator import GoogleTranslator
import re
import mysql.connector as sql
import os
from datetime import datetime, timedelta
from dateutil import parser


# MODIFY SCRAPED DATA
class JobscraperPipeline:
    def process_item(self, item, spider):
        translator = GoogleTranslator(source='cs', target='en')
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        # Strip whitespace for all spiders
        for field_name in field_names:
            value = adapter.get(field_name)
            if value and field_name != 'run_id':
                adapter[field_name] = value.strip()
        
        # LINKEDIN
        if spider.name == 'linkedin':
            # PUBLISHED DATE
            published = adapter.get('published')
            if published:
                if "today" in published.lower() or "hour" in published.lower() or "minute" in published.lower():
                    adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif "yesterday" in published.lower():
                    adapter["published"] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                elif "days" in published.lower() and "ago" in published.lower():
                    try:
                        published_days_ago = int(re.search(r'\d+', published).group())
                        adapter["published"] = (datetime.now() - timedelta(days=published_days_ago)).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif "weeks" in published.lower() and "ago" in published.lower():
                    try:
                        published_weeks_ago = int(re.search(r'\d+', published).group())
                        adapter["published"] = (datetime.now() - timedelta(weeks=published_weeks_ago)).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # JOBS.CZ
        if spider.name == 'jobs':
            # Translate Czech to English
            translate_keys = ['title', 'location', 'published']
            for key in translate_keys:
                try:
                    adapter[key] = translator.translate(adapter.get(key))
                except Exception:
                    pass

            # Fix published date
            published = adapter.get('published')
            if published:
                try:
                    day_of_month = int(re.search(r'\d+', published).group())
                except Exception:
                    day_of_month = None
                if "today" in published.lower() or "hour" in published.lower() or "minute" in published.lower():
                    adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif "yesterday" in published.lower():
                    adapter["published"] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                # Format August 30th or August 30
                elif day_of_month:
                    date_str_cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', published)
                    # If the month is January and the date is in December, we need to subtract a year
                    if datetime.now().month == 1 and "december" in published.lower():
                        parsed_date = parser.parse(date_str_cleaned) - timedelta(days=365)
                        adapter["published"] = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        adapter["published"] = parser.parse(date_str_cleaned).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Fix salary
            salary = adapter.get('salary')
            if salary:
                # Remove everything that is not a digit or space and strip
                salary = re.sub(r"[^\d\s]", "", salary).strip()
                # Add CZK back to the end
                salary = salary + " CZK"
                # Add - between the numbers
                adapter['salary'] = re.sub(r'(\d+\s\d+)\s+(\d+\s\d+)', r'\1-\2', salary)
            else:
                adapter["salary"] = ""
        
        # PRACE.CZ
        elif spider.name == 'prace':
            # Salary
            if not adapter.get('salary'):
                adapter['salary'] = ""
            
            # Translate Czech to English
            translate_keys = ['title', 'location', 'salary']
            for key in translate_keys:
                try:
                    adapter[key] = translator.translate(adapter.get(key))
                except Exception:
                    pass
            
            # Set todays date since there is no published date
            adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # STARTUPJOBS.CZ
        elif spider.name == 'startup':
            # Fix link
            if "startupjobs.cz" not in adapter.get('link'):
                adapter["link"] = "https://www.startupjobs.cz" + adapter.get('link')
            
            # Translate location to English
            try:
                adapter["location"] = translator.translate(adapter["location"])
            except Exception:
                pass

            # Set todays date since there is no published date
            adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # INDEED.COM
        elif spider.name == 'indeed':
            # Fix salary
            if not adapter.get('salary'):
                adapter['salary'] = ""

            # Fix link
            if "indeed.com" not in adapter.get('link'):
                adapter["link"] = "https://cz.indeed.com" + adapter.get('link')
            
            # Translate Czech to English
            translate_keys = ['location', 'published', "salary"]
            for key in translate_keys:
                try:
                    adapter[key] = translator.translate(adapter.get(key))
                except Exception:
                    pass
            
            # Fix published date
            published = adapter.get('published')
            if published:
                # "Posted n days ago"
                if "ago" in published.lower():
                    try:
                        published_days_ago = int(re.search(r'\d+', published).group())
                        published = datetime.now() - timedelta(days=published_days_ago)
                        adapter["published"] = published.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # "Today"
                else:
                    adapter["published"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
        return item

# SAVE TO MYSQL DATABASE
class SaveToMySQLPipeline:
    # Connect to DB
    def __init__(self):
        self.conn = sql.connect(
            host="localhost",
            user="bohdan",
            password=os.getenv("MYSQL_PASSWORD"),
            database="CZ_Job_Aggregator"
        )

        self.cur = self.conn.cursor()
    
    # INSERT INTO DB
    def process_item(self, item, spider):
        # CHECK IF THE ITEM IS ALREADY IN THE DATABASE
        self.cur.execute("""
        SELECT COUNT(*) FROM jobs_active WHERE title LIKE %s AND company LIKE %s OR link = %s
        """, (item["title"], item["company"], item["link"]))
        
        count = self.cur.fetchone()[0]
        # INSERT INTO DB IF ITEM IS VALID
        if count == 0 and item["title"] and item["company"] and item["link"]:
            self.cur.execute("""
            INSERT INTO jobs_active 
                (run_id,
                title, 
                link, 
                company, 
                location, 
                salary, 
                published, 
                source) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (
                    item["run_id"],
                    item["title"],
                    item["link"],
                    item["company"],
                    item["location"],
                    item["salary"],
                    item["published"],
                    item["source"]
                ))
            
            self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()