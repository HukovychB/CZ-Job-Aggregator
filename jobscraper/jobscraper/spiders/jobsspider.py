import scrapy
from jobscraper.items import JobsItem
from datetime import datetime, timedelta
import re

class JobsSpider(scrapy.Spider):
    # def __init__(self, name, location):
    #     super(JobsSpider, self).__init__(*args, **kwargs)
    #     self.name = name
    #     self.location = location
    #     self.start_urls = [f"https://www.jobs.cz/prace/{location}/{name}/?locality%5Bradius%5D=10"]

    name = "jobs"
    allowed_domains = ["jobs.cz"]
    start_urls = [f"https://www.jobs.cz/prace/praha/?q%5B%5D=Analyst&locality%5Bradius%5D=10"]

    def parse(self, response):
        jobs = response.css("article.SearchResultCard")

        for job in jobs:
            job_item = JobsItem()

            job_item["title"] = job.css("h2 a::text").get()
            job_item["link"] = job.css("h2 a::attr(href)").get()
            job_item["company"] = job.css(".SearchResultCard__footerItem:nth-child(1) span::text").get()
            job_item["location"] = job.xpath(".//footer/ul/li[2]/svg/following-sibling::text()").get()
            published = job.css(".SearchResultCard__header div[data-test-ad-status]::text").get()
            if published == "Doporučujeme" or "Dopor" in published or "Končí" in published or "Příležitost" in published:
                job_item["published"] = ""
            elif "dnes" in published or "hodin" in published:
                job_item["published"] = datetime.now().strftime("%Y-%m-%d")
            elif "včera" in published:
                job_item["published"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                job_item["published"] = published
            salary = job.css("span.Tag--success::text").get()
            if salary:
                salary = re.sub(r"[^\d\s]", "", salary)
                job_item["salary"] = salary + "Kč"
            else:
                job_item["salary"] = ""
            
            job_item["source"] = "jobs.cz"
            
            yield job_item

        # Go to the next page
        next_page = response.css("a.Pagination__button--next::attr(href)").get()

        if next_page:
            if "jobs.cz" not in next_page:
                next_page = "https://www.jobs.cz" + next_page

            yield response.follow(next_page, callback=self.parse)