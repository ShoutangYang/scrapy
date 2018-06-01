# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import  datetime
import re
from settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from scrapy.loader import  ItemLoader
from scrapy.contrib.loader.processor import TakeFirst,Join,MapCompose
from w3lib.html import remove_tags


User_Agent={
    '1',
    '2',
}
"""
item:
    - 为抓取数据容器
    - 类似ORM
    

"""

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass

def remove_splash(value):
    return value.replace('/','')

def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [ item.strip() for item in addr_list if item.strip()!='查看地图' ]

    return  ''.join(addr_list)

class JobboleArticleItem(scrapy.Item):

    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums =scrapy.Field()
    fav_nums = scrapy.Field()
    tags =scrapy.Field()
    content =scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                  insert into jobbole_article(title,url,create_date,fav_nums,comment_nums,praise_nums,content,tags,url_object_id)
                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                  """
        params=(
        self['title'], self['url'], self['create_date'], self['fav_nums'], self['comment_nums'],
        self['praise_nums'], self['content'], self['tags'], self['url_object_id']
        )

        return insert_sql,params

class LagouJobItem(scrapy.Item):
    title  = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
       input_processor= MapCompose(remove_splash),
    )

    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need =scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_desc = scrapy.Field(
    )
    job_addr=scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)
    )
    job_advantage = scrapy.Field()
    company_name =scrapy.Field()
    company_url=scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )

    crawl_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql="""
            insert into lagou_job(url_object_id,title,url,salary,job_city,work_years,degree_need,job_type,publish_time,job_advantage,job_addr,company_name,company_url,tags,job_desc,crawl_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE  salary = VALUES(salary),job_desc=VALUES(job_desc)
        """
        # ON DUPLICATE KEY UPDATE  salary = VALUES(salary),job_desc=VALUES(job_desc)
        params=(
            self['url_object_id'],self['title'],self['url'],self['salary'],self['job_city'],self['work_years'],self['degree_need'],self['job_type'],self['publish_time'],self['job_advantage'],
            self['job_addr'],self['company_name'],self['company_url'],self['tags'],self['job_desc'],self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql,params

class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

