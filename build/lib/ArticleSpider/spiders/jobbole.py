# -*- coding: utf-8 -*-
import scrapy
import  re
import datetime
from scrapy.http import Request
from urllib import  parse
from items import JobboleArticleItem

from selenium import webdriver
from scrapy.xlib.pydispatch import  dispatcher
from scrapy import signals

import hashlib
def get_md5(url):
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

"""
 - spider 入口
 - start_url 为爬取的连接
 - parse 下载连接后，将response 传递给该参数，该方法负责完成数据解析，
 
"""

class JobboleSpider(scrapy.Spider):

    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse_detail(self, response):
        """
        xpath 方式提取数据
        :param response:
        :return:
        """
        # title = response.xpath('//div[@class ="entry-header"]/h1/text()').extract_first('')
        # create_date = response.xpath('//div[@class="entry-meta"]/p/text()').extract()[0]
        # priase_num = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # fav_num = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*",fav_num)
        # if  match_re:
        #     fav_num = match_re.group(1)
        # print(fav_num)
        #
        # comment_num = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match('.*?(\d+).*',comment_num)
        # if  match_re:
        #     comment_num = match_re.group(1)
        #
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//div[@class="entry-meta"]/p/text()').extract()
        # tag_list =[element for element in tag_list if not element.strip().endswitch('评论')]
        # tag = ",".join(tag_list)

        """
        css 方式提取数据
        """

        front_image_url= response.meta.get('front_image_url','')
        title = response.css(".entry-header h1 ::text").extract()[0]
        create_date = response.css(".entry-meta p::text").extract()[0].strip().replace('·','').strip()
        fav_num = response.css('.bookmark-btn::text').extract()[0]
        priase_num  = response.css('.vote-post-up h10::text').extract()[0]

        match_re = re.match(".*?(\d+).*",fav_num)
        if  match_re:
            fav_num =int( match_re.group(1))
        else:
            fav_num = 0


        comment_num = response.css('a[href="#article-comment"] span ::text').extract()[0]
        if  match_re:
            comment_num = int(match_re.group(1))
        else:
            comment_num = 0

        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()

        tag_list =[element for element in tag_list if not element.strip().endswith('评论')]
        content = response.xpath('//div[@class="entry"]').extract()[0]



        tag = ",".join(tag_list)
        article_item= JobboleArticleItem()

        article_item['title']= title
        article_item['url_object_id'] = get_md5(response.url)

        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
                 create_date = datetime.datetime.now().date()

        article_item['create_date'] = create_date
        article_item['praise_nums']= priase_num
        article_item['fav_nums'] = fav_num
        article_item['content']=content
        article_item['comment_nums']= comment_num
        article_item['tags'] = tag
        article_item['front_image_url']=[front_image_url]
        article_item['url']=response.url
        article_item['url_object_id']=get_md5(response.url)

        yield  article_item

    def parse(self, response):
        post_urls = response.css("#archive .floated-thumb .post-thumb a")
        for post_url in post_urls:
            image_url = post_url.css('img::attr(src)').extract_first("")
            post_url = post_url.css('::attr(href)').extract_first('')
            print(post_url)
            yield Request(url=parse.urljoin(response.url, post_url),meta ={"front_image_url":image_url} ,callback=self.parse_detail)
        next_url = response.css(".next.page-numbers::attr(href)").extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
        pass

    def __init__(self):
            self.brower = webdriver.Chrome()
            super(JobboleSpider, self).__init__()
            dispatcher.connect(self.spider_closed,signals.spider_closed)

    def spider_closed(self,spider):
        print('browser is closed!')
        self.brower.quit()

