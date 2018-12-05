from scrapy.http import Request
from myspider.utils import get_config
from scrapy.spiders import CrawlSpider
from scrapy import FormRequest
from urllib import parse
import time
from scrapy.http.cookies import CookieJar
from myspider.items import WAPCNKIItem
from urllib import request
from urllib.error import HTTPError
from myspider.user_agent import USER_AGENT
import random
from http import cookiejar
from scrapy.http import FormRequest
from io import BytesIO

class WAPCNKISpider(CrawlSpider):
    name = 'wapcnki'

    def __init__(self, name, key_word, max_page, *args, **kwargs):
        self.list_url = 'http://wap.cnki.net/touch/web/Article/Search'
        self.header = {'Referer': 'http://wap.cnki.net/touch/web'}
        config = get_config(name)
        self.config = config
        self.key_word = key_word
        self.my_max_page = max_page
        self.page_size = 10
        self.myFormData = {#近十年的数据
            "searchtype":"0",
            "dbtype":"",
            "pageindex":"1",
            "pagesize": str(self.page_size),
            "theme_kw":"",
            "title_kw":"",
            "full_kw":"",
            "author_kw":"",
            "depart_kw":"",
            "key_kw":"",
            "abstract_kw":"",
            "source_kw":"",
            "teacher_md":"",
            "catalog_md":"",
            "depart_md":"",
            "refer_md":"",
            "name_meet":"",
            "collect_meet":"",
            "keyword":self.key_word,
            "remark":"",
            "fieldtype":"101",
            "sorttype":"0",
            "articletype":"10",
            "screentype":"0",
            "isscreen":"",
            "subject_sc":"",
            "research_sc":"",
            "depart_sc":"",
            "sponsor_sc":"",
            "author_sc":"",
            "teacher_sc":"",
            "subjectcode_sc":"",
            "researchcode_sc":"",
            "departcode_sc":"",
            "sponsorcode_sc":"",
            "authorcode_sc":"",
            "teachercode_sc":"",
            "starttime_sc":"2007",
            "endtime_sc":"2018",
            "timestate_sc":"1"
        }
        self.allowed_domains = config.get('allowed_domains')
        super(WAPCNKISpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        data = {
            "kw": self.key_word,
            "field":5
        }
        url = self.list_url + '?' + parse.urlencode(data)
        yield Request(url=url,
                      headers=self.header,
                      meta={'cookiejar': 1},
                      callback=self.parse)

    def parse(self, response):
        self.header['Referer'] = response.request.url
        yield FormRequest(url=self.list_url,
                          headers = self.header,
                          method = 'POST',
                          meta = {'cookiejar': 1},
                          formdata = self.myFormData,
                          callback = self.parse_list,
                          dont_filter = True)

    def parse_list(self, response):
        paper_size = int(response.xpath('//*[@id="totalcount"]/text()').extract_first())
        if not paper_size:
            paper_num = 0
        else:
            paper_num = int(((paper_size + self.page_size - 1) / self.page_size)) + 1
        if paper_num > self.my_max_page:
            paper_num = self.my_max_page
        print('total paper size: ' + str(paper_size))
        print('total paper_num: ' + str(paper_num))
        for page in range(1, paper_num):
            self.myFormData["pageindex"] = str(page),
            yield FormRequest(url=self.list_url,
                              headers = self.header,
                              method = 'POST',
                              meta = {'cookiejar': page+1, 'page': page},
                              formdata = self.myFormData,
                              callback = self.parse_list_link,
                              dont_filter = True)

    def parse_list_link(self, response):
        items = response.xpath('//a[@class="c-company-top-link"]/@href').extract()
        with open('../record_page.txt', 'a') as f:
            f.write(str(response.meta['page']) + '\n')
        for item in items:
            yield Request(url = item,
                          meta={'cookiejar': response.meta['cookiejar']},
                          headers = self.header,
                          callback = self.parse_item)

    def parse_item(self, response):
        item = WAPCNKIItem()
        url = response.request.url
        baseinfo = response.xpath('/html/body/div[@class="c-card__paper2"]')
        title = baseinfo.xpath('//div[@class="c-card__title2"]/text()').extract()
        online_date = baseinfo.xpath('///div[@class="c-card__subline"]/div[@class="c-card__date"]/text()').extract()
        author = baseinfo.xpath('//div[@class="c-card__subline"]/div[@class="c-card__author"]/a/text()').extract()
        abstract = baseinfo.xpath('//div[@class="c-card__aritcle"]/text()').extract()
        orgn = baseinfo.xpath('//div[contains(text(),"机　构")]/following-sibling::*/a/text()').extract()
        keywords = baseinfo.xpath('//div[contains(text(),"关键词")]/following-sibling::*/a/text()').extract()
        region = baseinfo.xpath('//div[contains(text(),"领　域")]/following-sibling::*/a/text()').extract()

        item['url'] = url
        item['title'] = ''.join(title).strip()
        item['online_date'] = ''.join(online_date).strip()
        item['author'] = [au.strip() for au in author]
        item['abstract'] = ''.join(abstract).strip()
        item['paper_type'] = "期刊"
        item['key_word'] = [ky.strip() for ky in keywords]
        item['abstract'] = ''.join(abstract).strip()
        item['search_word'] = self.key_word
        item['organization'] = [og.strip() for og in orgn]
        item['region'] = [rg.strip() for rg in region]
        yield item