import scrapy
from jobscraper.items import JobsItem

class PraceSpider(scrapy.Spider):
    # def __init__(self, name, location):
    #     super(PraceSpider, self).__init__(*args, **kwargs)
    #     self.name = name
    #     self.location = location
    #     self.start_urls = [f"https://www.prace.cz/hledat/?searchForm%5Bprofs%5D={name}"]

    name = "prace"
    allowed_domains = ["prace.cz"]
    start_urls = [f"https://www.prace.cz/hledat/?searchForm%5Bprofs%5D=analyst"]

    def parse(self, response):
        jobs = response.css("li.search-result__advert")

        for job in jobs:
            if not job.css("li#signUpWrapper"):
                job_item = JobsItem()

                job_item["title"] = job.css("h3 a strong::text").get()
                job_item["link"] = job.css("h3 a::attr(href)").get()
                job_item["company"] = job.xpath(".//div[@class='grid__item e-16']/div[@class='grid'][2]/div/div[2]/div/following-sibling::text()").get()
                job_item["location"] = job.xpath(".//div[@class='grid__item e-16']/div[@class='grid'][2]/div/div[1]/strong/text()").get()
                job_item["salary"] = job.xpath(".//span[@class='search-result__advert__box__item search-result__advert__box__item--salary']/span/following-sibling::text()").get()
                job_item["source"] = "prace.cz"

                yield job_item
            
        # Go to the next page
        next_page = response.css("span.page a::attr(href)").get()

        if not next_page:
            next_page = response.css("span.pager__next a::attr(href)").get()
        
        if next_page:
            if "prace.cz" not in next_page:
                next_page = "https://www.prace.cz" + next_page

            yield response.follow(next_page, callback=self.parse)