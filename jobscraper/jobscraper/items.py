# MODEL FOR SCRAPED ITEMS

import scrapy


class JobsItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    published = scrapy.Field()
    salary = scrapy.Field()
    source = scrapy.Field()
    run_id = scrapy.Field()
