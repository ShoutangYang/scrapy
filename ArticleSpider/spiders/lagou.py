# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import  ItemLoader
from util.common import  get_md5

import datetime
import requests
from settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT

from items import LagouJobItemLoader,ItemLoader,LagouJobItem
import  time
from hashlib import  sha1
import  json
import  base64
from  PIL import Image
import hmac
try:
    import cooklib
except:
    import http.cookiejar as cookielib

import  re
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")  # cookie存储文件，

from items import User_Agent



class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']

    custom_settings = {
    "COOKIES_ENABLED": False,
    "DOWNLOAD_DELAY": 4,
    'DEFAULT_REQUEST_HEADERS': {
        'HOST':'www.lagou.com',
        'Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Referer':'https://www.lagou.com/',
        'Origin':'https://www.lagou.com/',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',

        'Cookie':
            '_ga=GA1.2.1197943209.1527148298;'+
            'index_location_city=%E4%B8%8A%E6%B5%B7;'+
            '_gid=GA1.2.1596058823.1527337395;'+
            'WEBTJ-ID=20180526202359-1639c67cf2f90a-028181f7a8b3f2-39614807-1327104-1639c67cf30678;'+
            'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527148476,1527337395,1527337439;'+
            'LGSID=20180526202359-aacf4306-60df-11e8-a197-525400f775ce;'+
            'JSESSIONID=ABAAABAACEBACDG39F1CFEAAECF38CF438E944D685E83F6;'+
            'TG-TRACK-CODE=index_navigation;'+
            '_gat=1;'+
            'SEARCH_ID=cf51752d32ac49918d5d9edef16ba74e;'+
            'LGRID=20180526214849-8496acd8-60eb-11e8-a1a8-525400f775ce;'+
            'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527342529;'+
            'X_HTTP_TOKEN:9962314dca0dfa4946e5c996595ed6e6;'+
             'user_trace_token=20180524155330-d2c0567c-6831-45a5-ad51-8275dd8cd902;'+
            'LGUID=20180524155459-c1f8dcb3-5f27-11e8-8a9c-5254005c3644;'

    }
    }
    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*',)),follow=True),
        Rule(LinkExtractor(allow=('gongsi/j\d+.html',)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),


    )

    def parse_item(self, response):
        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()

        self.logger('hi.this is an item page! %s',response.url)

        # item = scrapy.Item()
        # item['id'] = response.xpath()

        return i

    def parse_job(self,response):
        item_loder = LagouJobItemLoader(item = LagouJobItem(),response = response)

        item_loder.add_css("title",'.job-name::attr(title)')
        item_loder.add_value('url',response.url)
        item_loder.add_value('url_object_id',get_md5(response.url))
        item_loder.add_css("salary",'.job_request .salary::text')
        item_loder.add_xpath('job_city','//*[@class="job_request"]/p/span[2]/text()')
        item_loder.add_xpath('work_years','//*[@class="job_request"]/p/span[3]/text()')

        item_loder.add_xpath("degree_need",'//*[@class="job_request"]/p/span[4]/text()')

        item_loder.add_xpath("job_type",'//*[@class="job_request"]/p/span[5]/text()')

        item_loder.add_css('tags','.position-label li::text')
        item_loder.add_css('publish_time','.publish_time::text')
        item_loder.add_css("job_advantage",".job-advantage p::text")
        item_loder.add_css('job_desc',".job_bt div ")
        item_loder.add_css('job_addr','.work_addr ')
        item_loder.add_css("company_name","#job_company dt a img::attr(alt)")
        item_loder.add_css("company_url","#job_company dt a::attr(href)")

        item_loder.add_value("crawl_time",datetime.datetime.now())

        job_item = item_loder.load_item()

        yield job_item
