# Helpers functions for the app

from twisted.internet import asyncioreactor
asyncioreactor.install()

import os 
from flask import redirect, session
from functools import wraps
import crochet
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import mysql.connector as sql
from deep_translator import GoogleTranslator

from jobscraper.jobscraper.spiders.jobsspider import JobsSpider
from jobscraper.jobscraper.spiders.indeedspider import IndeedSpider
from jobscraper.jobscraper.spiders.linkedinspider import LinkedinSpider
from jobscraper.jobscraper.spiders.pracespider import PraceSpider
from jobscraper.jobscraper.spiders.startupjobsspider import StartupSpider


def login_required(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Set scrapy settings module to work properly with FLASK
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'jobscraper.jobscraper.settings')

# SETUP CHROCHET
crochet.setup()

# List to store all CrawlerProcess instances
crawler_processes = []

@crochet.run_in_reactor
def run_spider(spider, job_name, location, run_id):
    """
    Run the spider in the reactor.
    """
    global crawler_processes
    process = CrawlerProcess(get_project_settings())
    crawler_processes.append(process)
    return process.crawl(spider, job=job_name, location=location, run_id=run_id)

def stop_all_spiders():
    """
    Stop all running spiders.
    """
    global crawler_processes
    for process in crawler_processes:
        process.stop()
    crawler_processes.clear()

def get_db_connection():
    """
    Return a connection to the database.
    """
    conn = sql.connect(
        host="localhost",
        user="bohdan",
        password=os.getenv("MYSQL_PASSWORD"),
        database="CZ_Job_Aggregator"
    )
    return conn

def fetch_jobs_from_db(job_name, location):
    """
    Fetch already existing jobs from the database based on the job name and location.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs_active WHERE title LIKE %s AND location LIKE %s AND published IS NOT NULL", ('%' + job_name + '%', '%' + location + '%'))
    jobs = cur.fetchall()
    conn.close()
    jobs = [
        {
            'id': job[0],
            'run_id': job[1],
            'time': job[2],
            'title': job[3],
            'link': job[4],
            'company': job[5],
            'location': job[6],
            'salary': job[7],
            'published': job[8].strftime('%a, %d %b'),
            'source': job[9]
        }
        for job in jobs
    ]

    return jobs

def fetch_new_jobs_from_db(run_id, location):
    """
    Fetch new jobs from the database that are dynamically added by spiders based on the run_id and location.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs_active WHERE run_id = %s AND location LIKE %s AND published IS NOT NULL", (run_id, '%' + location + '%'))
    jobs = cur.fetchall()
    conn.close()
    jobs = [
        {
            'id': job[0],
            'run_id': job[1],
            'time': job[2],
            'title': job[3],
            'link': job[4],
            'company': job[5],
            'location': job[6],
            'salary': job[7],
            'published': job[8].strftime('%a, %d %b'),
            'source': job[9]
        }
        for job in jobs
    ]

    return jobs

def add_job_to_favorites(job_data):
    """
    Add a job to the user's favorites in the database.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users_logs WHERE username = %s", (session.get("user_id"), ))
        user_id = cur.fetchall()[0][0]
        
        # Check if the job already exists for the user
        cur.execute("SELECT COUNT(*) FROM favorite_jobs WHERE user_id = %s AND title = %s AND link = %s AND company = %s AND location = %s AND published = %s",
                    (user_id, 
                    job_data['title'], 
                    job_data['link'], 
                    job_data['company'], 
                    job_data['location'],
                    job_data['published']))
        
        # Insert the job if it does not exist
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO favorite_jobs (user_id, title, link, company, location, salary, published) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (user_id, 
                        job_data['title'], 
                        job_data['link'], 
                        job_data['company'], 
                        job_data['location'], 
                        job_data['salary'], 
                        job_data['published']))
            
            conn.commit()
            return True
        else:
            return True
    except sql.Error:
        return False
    finally:
        cur.close()
        conn.close()
    
def remove_job_from_favorites(job_data):
    """
    Remove a job from the user's favorites in the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users_logs WHERE username = %s", (session.get("user_id"), ))
        user_id = cur.fetchall()[0][0]
        
        cur.execute("DELETE FROM favorite_jobs WHERE user_id = %s AND title = %s AND link = %s AND company = %s AND location = %s AND published = %s",
                    (user_id,
                    job_data['title'],
                    job_data['link'],
                    job_data['company'],
                    job_data['location'],
                    job_data['published']))
        
        conn.commit()
        return True
    except sql.Error:
        return False
    finally:
        cur.close()
        conn.close()

def update_job_status_in_db(job_data):
    """
    Update a job status in the database.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users_logs WHERE username = %s", (session.get("user_id"), ))
        user_id = cur.fetchall()[0][0]
        
        cur.execute("UPDATE favorite_jobs SET status = %s WHERE user_id = %s AND title = %s AND link = %s AND company = %s AND location = %s AND published = %s",
                    (job_data['status'],
                    user_id,
                    job_data['title'],
                    job_data['link'],
                    job_data['company'],
                    job_data['location'],
                    job_data['published']))
        
        conn.commit()
        return True
    except sql.Error:
        return False
    finally:
        cur.close()
        conn.close()
    
def fetch_my_jobs_from_db():
    """
    Fetch all jobs from the user's favorites in the database.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users_logs WHERE username = %s", (session.get("user_id"), ))
        user_id = cur.fetchall()[0][0]

        cur.execute("SELECT * FROM favorite_jobs WHERE user_id = %s", (user_id,))
        jobs = cur.fetchall()
        conn.close()
        jobs = [
            {
                'id': job[0],
                'title': job[3],
                'link': job[4],
                'company': job[5],
                'location': job[6],
                'salary': job[7],
                'published': job[8],
                'status': job[9]
            }
            for job in jobs
        ]
        return jobs
    except sql.Error:
        return [] 
    finally:
        cur.close()
        conn.close()


def remove_duplicates(list1, list2):
    """
    Remove all items from list1 that are already in list2.
    """
    list2_set = {tuple(sorted(d.items())) for d in list2}
    return [d for d in list1 if tuple(sorted(d.items())) not in list2_set]

def lookup_jobs(job_name, location, sites, run_id):
    """
    Lookup jobs based on the job name, location, sites, and run_id .
    """
    cz_translator = GoogleTranslator(target='cs')
    en_translator = GoogleTranslator(target='en')
    
    # Run the spider till finish
    if "jobs" in sites:
        # Works only with cities in czech
        location_jobs = cz_translator.translate(location)
        run_spider(JobsSpider, job_name, location_jobs, run_id)
    if "indeed" in sites:
        run_spider(IndeedSpider, job_name, location, run_id)
    if "linkedin" in sites:
        # Works only with cities in english
        location_linkedin = en_translator.translate(location)
        run_spider(LinkedinSpider, job_name, location_linkedin, run_id)
    if "prace" in sites:
        # We will select jobs only from desired location
        location_prace = cz_translator.translate(location)
        run_spider(PraceSpider, job_name, location_prace, run_id)
    if "startup" in sites:
        run_spider(StartupSpider, job_name, location, run_id)