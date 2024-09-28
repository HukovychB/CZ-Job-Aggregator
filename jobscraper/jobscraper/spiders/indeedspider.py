# INDEED SPIDER

import scrapy
from jobscraper.jobscraper.items import JobsItem


class IndeedSpider(scrapy.Spider):
    def __init__(self, job=None, location=None, run_id=None, *args, **kwargs):
        super(IndeedSpider, self).__init__(*args, **kwargs)
        self.job = job.strip().replace(" ", "+")
        self.location = location.strip()
        self.start_urls = [f"https://cz.indeed.com/jobs?q={self.job}&l={self.location}"]
        self.run_id = run_id

    name = "indeed"
    allowed_domains = ["cz.indeed.com", "proxy.scrapeops.io"]

    def parse(self, response):
        # Select all job cards
        jobs = response.css("div.mosaic-provider-jobcards ul li")

        # Loop through each job card and extract the data
        for job in jobs:
            job_item = JobsItem()
            title = job.css("h2.jobTitle a span::text").get()
            if not title:
                continue
            job_item["title"] = title
            job_item["link"] = job.css("h2.jobTitle a::attr(href)").get()
            job_item["company"] = job.xpath(".//span[@data-testid='company-name']/text()").get()
            job_item["location"] = job.xpath(".//div[@data-testid='text-location']/text()").get()
            job_item["published"] = job.xpath(".//span[@data-testid='myJobsStateDate']/span/following-sibling::text()").get()
            job_item["salary"] = job.css(".salary-snippet-container div::text").get()
            job_item["source"] = "indeed.com"
            job_item["run_id"] = self.run_id

            yield job_item
        
        # Go to the next page and repeat
        next_page = response.xpath("//a[@data-testid='pagination-page-next']/@href").get()

        if next_page:
            if "cz.indeed.com" not in next_page:
                next_page = "https://cz.indeed.com" + next_page

            yield response.follow(next_page, callback=self.parse)

