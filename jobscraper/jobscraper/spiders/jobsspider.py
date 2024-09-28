# JOBS.CZ SPIDER

import scrapy
from jobscraper.jobscraper.items import JobsItem

class JobsSpider(scrapy.Spider):
    def __init__(self, job=None, location=None, run_id=None, *args, **kwargs):
        super(JobsSpider, self).__init__(*args, **kwargs)
        self.job = job.strip().replace(" ", "+")
        self.location = location.strip().replace(" ", "-").lower()
        self.start_urls = [f"https://www.jobs.cz/prace/{self.location}/?q%5B%5D={self.job}&locality%5Bradius%5D=10"]
        self.run_id = run_id

    name = "jobs"
    allowed_domains = ["jobs.cz", "proxy.scrapeops.io"]

    def parse(self, response):
        # SELECT JOB CARDS
        jobs = response.css("article.SearchResultCard")

        # ITERATE OVER JOB CARDS AND EXTRACT DATA
        for job in jobs:
            job_item = JobsItem()

            job_item["title"] = job.css("h2 a::text").get()
            job_item["link"] = job.css("h2 a::attr(href)").get()
            job_item["company"] = job.css(".SearchResultCard__footerItem:nth-child(1) span::text").get()
            job_item["location"] = job.xpath(".//footer/ul/li[2]/svg/following-sibling::text()").get()
            job_item["published"] = job.css(".SearchResultCard__header div[data-test-ad-status]::text").get()
            job_item["salary"] = job.css("span.Tag--success::text").get()
            job_item["source"] = "jobs.cz"
            job_item["run_id"] = self.run_id
            
            yield job_item

        # Go to the next page and repeat
        next_page = response.css("a.Pagination__button--next::attr(href)").get()

        if next_page:
            if "jobs.cz" not in next_page:
                next_page = "https://www.jobs.cz" + next_page

            yield response.follow(next_page, callback=self.parse)