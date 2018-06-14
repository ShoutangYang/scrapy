# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import  datetime
import re
from settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from models.es_types import ArticcleType,LagouType
from w3lib.html import remove_tags

from scrapy.loader import  ItemLoader
from scrapy.contrib.loader.processor import TakeFirst,Join,MapCompose
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticcleType._doc_type.using)

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

    def save_to_es(self):
        article = ArticcleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])

        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self['front_image_path']
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self['fav_nums']
        article.comment_nums = self["comment_nums"]
        article.tags = self['tags']
        article.meta.id = self['url_object_id']

        article.suggest=gen_suggests(ArticcleType._doc_type.index,((article.title,10),(article.tags,7)))

        article.save()
        pass

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

    def save_to_es(self):
        job = LagouType()
        job.title = self['title']
        job.url = self['url']
        job.meta.id = self['url_object_id']
        job.salary = self['salary']
        job.job_city = self['job_city']
        job.work_years =self['job_city']
        job.work_years =self['work_years']
        job.degree_need =self['degree_need']
        job.job_type = self['job_type']
        job.publish_time  =self['publish_time']
        job.job_desc = remove_tags(self['job_desc'])
        job.job_addr = self['job_addr']
        job.job_advantage = self['job_advantage']
        job.company_name = self['company_name']
        job.company_url= self['company_url']
        job.tags = self['tags']
        job.crawl_time = self['crawl_time']

        job.save()
        pass

class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def gen_suggests(index,info_tuple):
    """
     根据字符串生成搜索建议
     - set 为了去重
     -  注意里面的参数，详见api.此处容易踩坑
     - 调用 API可以参照kibana
    :param index:
    :param info_tuple:
    :return:
    """
    used_words= set()
    suggests =[]

    for text,weight in info_tuple:
        if text:
            words= es.indices.analyze(index=index,params={'filter':["lowercase"]},body={"text":text,"analyzer":'ik_max_word'})
            anylyzed_words=set([r['token'] for r in words["tokens"] if len(r['token'])>1 ])
            new_words = anylyzed_words- used_words
        else:
            new_words =set()
        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})

    return  suggests


    pass