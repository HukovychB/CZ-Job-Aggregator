# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobsItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    published = scrapy.Field()
    salary = scrapy.Field()
    source = scrapy.Field()
