# -*- coding:utf-8 -*-
__author__ = 'Tony.Yang'

from  datetime import datetime

from elasticsearch_dsl import DocType,Nested,Boolean,\
    analyzer,Completion,Keyword,Text,Date,Text,Integer

from  elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):

    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer('ik_max_word',filter=["lowercase"])

class ArticcleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')


    class Meta:
        index = "jobbole"
        doc_type="article"


class LagouType(DocType):
    title = Text(analyzer='ik_max_word')
    url = Keyword()
    url_object_id = Keyword()
    salary = Keyword()
    job_city= Keyword()
    work_years = Keyword()
    degree_need = Keyword()
    job_type = Keyword()
    publish_time = Keyword()
    job_desc = Text(analyzer='ik_max_word')
    job_addr = Keyword()
    job_advantage = Text(analyzer='ik_max_word')
    company_name = Keyword()
    company_url=Keyword()
    tags = Text(analyzer='ik_max_word')
    crawl_time = Date()

    class Meta:
        index = 'lagou'
        doc_type ='job'


if __name__ == '__main__':
   # LagouType().init()
   #
   # test = LagouType()
   # test.title='python'
   # test.company_url='url'
   # test.tags='tsgs'
   # test.crawl_time='time'
   # test.company_name='company'
   # test.job_advantage='advantage'
   # test.job_desc='desc'
   # test.publish_time='publish-time'
   # test.degree_need='degree-need'
   # test.work_years= 'years'
   # test.crawl_time= datetime.now()
   #
   #
   # test.save()
    ArticcleType.init()


