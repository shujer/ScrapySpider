# -*- coding: utf-8 -*-

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WanfangItem(scrapy.Item):
    url = scrapy.Field()
    c_title = scrapy.Field()
    e_title = scrapy.Field()
    doi = scrapy.Field()
    c_author = scrapy.Field()
    e_author = scrapy.Field()
    c_abstract = scrapy.Field()
    e_abstract = scrapy.Field()
    key_word = scrapy.Field()
    online_date = scrapy.Field()