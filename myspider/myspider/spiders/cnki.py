from scrapy.http import Request
from myspider.utils import get_config
from scrapy.spiders import CrawlSpider
from urllib import parse
import time
from scrapy.http.cookies import CookieJar
from myspider.items import CNKIItem
from urllib import request
from urllib.error import HTTPError
from myspider.user_agent import USER_AGENT
import random
from http import cookiejar

def check_redirect(url, ref):
    try:
        cj = cookiejar.CookieJar()
        opener = request.build_opener(request.HTTPCookieProcessor(cj))
        request.install_opener(opener)
        req = request.Request(url)
        req.add_header('Referer', ref)
        req.add_header('User-Agent', random.choice(USER_AGENT))
        req.add_header('Content-Type', 'text/html; charset=utf-8')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
        response = request.urlopen(req)
        if response.status == 302 and 'Location' in response.headers:
            redirect_url = str(response.headers['Location'], encoding='utf=8')
            return redirect_url
        else:
            return url
    except HTTPError as e:
        print("redirect error!" + e.msg)
        return None


class CNKISpider(CrawlSpider):
    name = 'cnki'

    def __init__(self, name, key_word, max_page, *args, **kwargs):
        self.base_url = 'http://kns.cnki.net'
        self.home_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&'
        self.list_url = 'http://kns.cnki.net/kns/brief/brief.aspx'
        self.cur_referer = 'http://kns.cnki.net/kns/brief/default_result.aspx'
        config = get_config(name)
        self.config = config
        self.key_word = key_word
        self.my_max_page = max_page
        self.allowed_domains = config.get('allowed_domains')
        super(CNKISpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        data = {
            "formDefaultResult": "",
            "PageName": "ASP.brief_default_result_aspx",
            "DbCatalog": "中国学术文献网络出版总库",
            "ConfigFile": "SCDBINDEX.xml",
            "txt_1_sel": "SU$%=|",
            "txt_1_value1": self.key_word,
            "DbPrefix": "SCDB",
            "db_opt": "CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CJRF,CJFN,CCJD",
            "singleDB": "SCDB",
            "db_codes": "CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CJRF,CJFN,CCJD",
            "his": 0,
            "txt_1_special1": "%",
            "ua": "1.11",
            "__": time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        }
        query_string = parse.urlencode(data)
        yield Request(url=self.home_url+query_string,
                      headers={"Referer": self.cur_referer},
                      cookies={CookieJar: 1},
                      callback=self.parse)

    def parse(self, response):
        data = {
            'pagename': 'ASP.brief_default_result_aspx',
            'dbPrefix': 'SCDB',
            'dbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'research': 'off',
            't': int(time.time()),
            'keyValue': self.key_word,
            'S': '1'
        }
        query_string = parse.urlencode(data)
        url = self.list_url + '?' + query_string
        yield Request(url=url,
                      headers={"Referer": self.cur_referer},
                      meta={"ref": url},
                      callback=self.parse_list_first)

    def parse_list_first(self, response):
        page_link = response.xpath('//span[@class="countPageMark"]/text()').extract_first()
        self.cur_referer = response.request.url
        # self.parse_paper_link(response)
        max_page = int(page_link.split("/")[1])
        for page_num in range(2, max_page+1):
            if page_num < self.my_max_page:
                half_url = response.xpath('//div[@class="TitleLeftCell"]/a[contains(text(),"下一页")]/@href').extract_first()
                data = {
                    "curpage": page_num,
                    "RecordsPerPage": 20,
                    "QueryID": 0,
                    "ID":"",
                    "turnpage": 1,
                    "tpagemode": "L",
                    "dbPrefix": "SCDB",
                    "Fields":"",
                    "DisplayMode": "listmode",
                    "PageName": "ASP.brief_default_result_aspx",
                    "isinEn": 1
                }
                query_string = parse.urlencode(data)
                url = self.list_url + '?' + query_string
                print("prepare to crawl page:" + url)
                yield Request(url=url,
                              headers={"Referer": self.cur_referer},
                              callback=self.parse_paper_link)
                self.cur_referer = url
        self.parse_paper_link(response)

    def parse_paper_link(self, response):
        refer = response.request.url
        tr_node = response.xpath("//tr[@bgcolor='#f6f7fb']|//tr[@bgcolor='#ffffff']")
        for item in tr_node:
            paper_link = item.xpath("td/a[@class='fz14']/@href").extract()
            paper_pub_date = ''.join(item.xpath("td[5]/text()").extract()).strip()
            paper_type = ''.join(item.xpath("td[6]/text()").extract()).strip()
            for href in paper_link:
                flag_url = check_redirect(self.base_url+href, refer)
                if flag_url:
                    yield Request(url=flag_url,
                                  headers={"Referer": refer},
                                  callback=self.parse_item,
                                  meta={"cnkiitem": {"paper_pub_date": paper_pub_date, "paper_type": paper_type}})
                else:
                    continue

    def parse_item(self, response):
        item = CNKIItem()
        url = response.request.url
        title = response.xpath('//*[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxTitle"]/h2/text()').extract()
        author = response.xpath('//*[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="author"]/span/a/text()').extract()
        orgn = response.xpath('//*[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="orgn"]/span/a/text()').extract()
        abstract = response.xpath('//*[@id="ChDivSummary"]/text()').extract()
        keywords = response.xpath('//*[@id="catalog_KEYWORD"]/following-sibling::*/text()').extract()
        item['online_date'] = response.meta["cnkiitem"]["paper_pub_date"]
        item['paper_type'] = response.meta["cnkiitem"]["paper_type"]
        item['key_word'] = [ky.strip() for ky in keywords]
        item['abstract'] = ''.join(abstract).strip()
        item['url'] = url
        item['title'] = ''.join(title).strip()
        item['author'] = [au.strip() for au in author]
        item['search_word'] = self.key_word
        item['organization'] = [og.strip() for og in orgn]
        yield item



