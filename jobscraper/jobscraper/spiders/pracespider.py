# PRACE.CZ SPIDER

import scrapy
from jobscraper.jobscraper.items import JobsItem

class PraceSpider(scrapy.Spider):
    def __init__(self, job=None, location=None, run_id=None, *args, **kwargs):
        super(PraceSpider, self).__init__(*args, **kwargs)
        self.job = job.strip().replace(" ", "+")
        # No location parameter for prace.cz
        self.start_urls = [f"https://www.prace.cz/hledat/?searchForm%5Bprofs%5D={self.job}"]
        self.run_id = run_id

    name = "prace"
    allowed_domains = ["prace.cz", "proxy.scrapeops.io"]

    def parse(self, response):
        # Select all job cards
        jobs = response.css("li.search-result__advert")

        # Loop through each job card and extract the data
        for job in jobs:
            if not job.css("li#signUpWrapper"):
                job_item = JobsItem()

                job_item["title"] = job.css("h3 a strong::text").get()
                job_item["link"] = job.css("h3 a::attr(href)").get()
                job_item["company"] = job.xpath(".//div[@class='search-result__advert__box__item search-result__advert__box__item--company ']/div/following-sibling::text()").get()
                location = job.xpath(".//div[@class='search-result__advert__box__item search-result__advert__box__item search-result__advert__box__item--location']/strong/text()").get()
                if location:
                    if self.location in location.lower():
                        job_item["location"] = location
                    else:
                        job_item["location"] = ""
                else:
                    job_item["location"] = ""
                job_item["salary"] = job.xpath(".//span[@class='search-result__advert__box__item search-result__advert__box__item--salary']/span/following-sibling::text()").get()
                job_item["published"] = ""
                job_item["source"] = "prace.cz"
                job_item["run_id"] = self.run_id

                yield job_item
            
        # Go to the next page
        next_page = response.css("span.page a::attr(href)").get()

        if not next_page:
            next_page = response.css("span.pager__next a::attr(href)").get()
        
        if next_page:
            if "prace.cz" not in next_page:
                next_page = "https://www.prace.cz" + next_page

            yield response.follow(next_page, callback=self.parse)