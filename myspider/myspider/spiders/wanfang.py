# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from myspider.items import WanfangItem
from myspider.utils import get_config


class WanfangSpider(scrapy.Spider):
    name = 'wanfang'

    def __init__(self, name, *args, **kwargs):
        self.base_url = 'http://s.wanfangdata.com.cn/Paper.aspx?'
        config = get_config(name)
        self.config = config
        self.key_word = config.get('KEY_WORD')
        self.my_max_page = config.get('MAX_PAGE')
        self.allowed_domains = config.get('allowed_domains')
        super(WanfangSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        start_url = self.base_url + 'q=' + self.key_word + '&f=top&p=1'
        yield Request(url=start_url, callback=self.parse)

    def parse(self, response):
        page_link = response.xpath('//div[@class="right"]/div[@class="record-item-list"]/p[@class="pager"]/span[@class="page_link"]/text()').extract_first()
        print(page_link)
        max_page = int(page_link.split("/")[1])
        print(max_page)
        for index in range(1, max_page):
            url = self.base_url + 'q=' + self.key_word + '&f=top&p=' + str(index)
            if index < self.my_max_page :
                yield Request(url=url, callback=self.parse_result, dont_filter=True)

    def parse_result(self, response):
        url_list = response.xpath('//div[@class="record-item-list"]/div[@class="record-item"]/div[@class="left-record"]/div[@class="record-title"]/a[@class="title"]/@href').extract()
        for url in url_list:
            yield Request(url=url, callback=self.parse_info, meta={'refer': url}, dont_filter=True)

    def parse_info(self, response):
        item = WanfangItem()
        baseinfo = response.xpath('//div[@class="fixed-width baseinfo clear"]/div[@class="section-baseinfo"]')
        c_title = baseinfo.xpath('//h1/text()').extract()
        e_title = baseinfo.xpath('//h2/text()').extract()
        abstract = response.xpath('//div[@class="baseinfo-feild abstract"]')
        c_abstract = abstract.xpath('//div[@class="row clear zh"]/div[@class="text"]/text()').extract()
        e_abstract = abstract.xpath('//div[@class="row clear fl"]/div[@class="text"]/text()').extract()
        c_abstract_short = response.xpath('/html/body/div[3]/div/div[2]/div[2]/div[1]/text()').extract()
        content = response.xpath('//div[@class="fixed-width-wrap fixed-width-wrap-feild"]/div[@class="fixed-width baseinfo-feild"]')
        doi = content.xpath('//span[contains(text(),"doi")]/following-sibling::*[1]/a/text()').extract()
        c_author = content.xpath('//span[contains(text(),"作者：")]/following-sibling::*[1]/a/text()').extract()
        e_author = content.xpath('//span[contains(text(),"Author")]/following-sibling::*[1]/span/text()').extract()
        key_word = content.xpath('//div[@class="row row-keyword"]/span[@class="text"]//text()').extract()
        online_date = content.xpath('//span[contains(text(),"在线出版日期：")]/following-sibling::*[1]/text()').extract()

        item['url'] = response.meta['refer']
        item['c_title'] = ''.join(c_title).strip()
        item['e_title'] = ''.join(e_title).strip()
        item['doi'] = ''.join(doi).strip()
        item['c_author'] = [''.join(author).strip() for author in c_author]
        item['e_author'] = [''.join(author).strip() for author in e_author]
        item['key_word'] = [''.join(word).strip() for word in key_word]
        item['online_date'] = ''.join(online_date).strip()
        c_abstract_1 = ''.join(c_abstract).strip();
        c_abstract_2 = ''.join(c_abstract_short).strip();
        if c_abstract_1 != "":
            item['c_abstract'] = c_abstract_1
        else:
            item['c_abstract'] = c_abstract_2

        item['e_abstract'] = ''.join(e_abstract).strip();

        yield item
