import scrapy

class LinkedinSpider(scrapy.Spider):
    name = "linkedin"
    llowed_domains = ["https://www.linkedin.com/jobs/search?"]
    start_urls = ["https://www.linkedin.com/jobs/search?"]

    def parse(self, response):
        pass