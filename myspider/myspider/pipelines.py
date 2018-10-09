# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import re
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

def chineseClean(input):
    input = re.sub('\n+', " ", input)
    input = re.sub('\u3000\u3000+', "\n", input)
    return input

def englishClean(input):
    input = re.sub('\n+', " ", input)
    input = re.sub('\u3000\u3000+', "\n", input)
    input = re.sub(' +', " ", input)
    return input


def removeUselessValue(array):
    return [i for i in array if (i != '' and i != '[1]' and i != '[2]' and i != '[3]' and i != '[4]')]


class WanfangPipeline(object):
    def process_item(self, item, spider):
        if item['key_word']:
            item['key_word'] = removeUselessValue(item['key_word'])
        if item['c_author']:
            item['c_author'] = removeUselessValue(item['c_author'])
        if item['e_author']:
            item['e_author'] = removeUselessValue(item['e_author'])
        if item['c_abstract']:
            item['c_abstract'] = chineseClean(item['c_abstract'])
        if item['e_abstract']:
            item['e_abstract'] = englishClean(item['e_abstract'])
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        if self.db[name].find_one({'url': item['url']}):
            self.db[name].update({'url': item['url']},{'$set': dict(item)})
        else:
            self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()



class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item 

    def get_media_requests(self, item, info):
        yield Request(item['url'])

