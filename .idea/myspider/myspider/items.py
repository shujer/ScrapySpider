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
    c_key_word = scrapy.Field()
    e_key_word = scrapy.Field()
    online_date = scrapy.Field()
    search_word = scrapy.Field()


class CNKIItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    doi = scrapy.Field()
    author = scrapy.Field()
    abstract = scrapy.Field()
    key_word = scrapy.Field()
    organization = scrapy.Field()
    online_date = scrapy.Field()
    search_word = scrapy.Field()
    paper_type = scrapy.Field()


class WAPCNKIItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    abstract = scrapy.Field()
    key_word = scrapy.Field()
    organization = scrapy.Field()
    online_date = scrapy.Field()
    search_word = scrapy.Field()
    paper_type = scrapy.Field()
    region = scrapy.Field()