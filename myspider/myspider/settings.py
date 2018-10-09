# -*- coding: utf-8 -*-

BOT_NAME = 'myspider'

SPIDER_MODULES = ['myspider.spiders']
NEWSPIDER_MODULE = 'myspider.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    #'myspider.middlewares.SpiderDownloaderMiddleware': 543,
    'myspider.middlewares.RandomUserAgentMiddleware': 401,
    'myspider.middlewares.ABProxyMiddleware': 1,
}

AB_PROXY_SERVER = {
    'proxyServer': "http://http-dyn.abuyun.com:9020",
    'proxyUser': "HN65ST45CP1923YD",
    'proxyPass': "8E2E9CC8C58F0206"
}
# Configure item pipelines
# ITEM_PIPELINES = {
#     'myspider.pipelines.MongoPipeline': 400,
#     'myspider.pipelines.WanfangPipeline': 300,
# }
#
# MONGO_URI='mongodb://47.106.173.16:27017'
# MONGO_DB='Spider'
#
# KEY_WORD = '岭南 传统建筑'
# MAX_PAGE = 30





