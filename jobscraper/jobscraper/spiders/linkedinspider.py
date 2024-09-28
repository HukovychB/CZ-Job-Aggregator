# LINKEDIN SPIDER

import scrapy
from jobscraper.jobscraper.items import JobsItem

class LinkedinSpider(scrapy.Spider):
    def __init__(self, job=None, location=None, run_id=None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        self.job = job.strip().replace(" ", "+")
        self.location = location.strip().replace(" ", "+")
        self.start_urls = [f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={self.job}&location={self.location}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&start="]
        self.run_id = run_id

    name = "linkedin"
    allowed_domains = ["linkedin.com", "proxy.scrapeops.io"]

    def start_requests(self):
        first_job_on_page = 0
        first_url = self.api_url + str(first_job_on_page)
        yield scrapy.Request(url=first_url, callback=self.parse, meta={'first_job_on_page': first_job_on_page})

    def parse(self, response):
        first_job_on_page = response.meta['first_job_on_page']
        # Select job cards
        jobs = response.css("li")
        
        # Iterate over job cards and extract data
        for job in jobs:
            job_item = JobsItem()
            job_item['title'] = job.css("h3::text").get(default='')
            job_item['link'] = job.css(".base-card__full-link::attr(href)").get(default='')
            job_item['company'] = job.css('h4 a::text').get(default='')
            job_item['location'] = job.css('.job-search-card__location::text').get(default='')
            job_item['published'] = job.css('time::text').get(default='')
            job_item['source'] = 'linkedin.com'
            job_item["run_id"] = self.run_id

            yield job_item
        
        # Go to the next page and repeat
        if len(jobs) > 0:
            first_job_on_page = int(first_job_on_page) + 25
            next_url = self.api_url + str(first_job_on_page)
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'first_job_on_page': first_job_on_page})