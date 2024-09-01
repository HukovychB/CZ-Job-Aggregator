import scrapy

class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["https://www.jobs.cz/"]
    start_urls = ["https://www.jobs.cz/"]

    def parse(self, response):
        pass