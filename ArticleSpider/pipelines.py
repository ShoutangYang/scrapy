# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
import codecs
import  json
from scrapy.exporters import JsonItemExporter
import  MySQLdb
from twisted.enterprise import adbapi
import  MySQLdb.cursors
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from models.es_types import ArticcleType
from w3lib.html import remove_tags



class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class ArticleImaesPipline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path=value['path']
        item['front_image_path']  = image_file_path

        return  item

class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self,item,spider):
        lines = json.dump(dict(item),ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()

class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False )
        self.exporter.start_exporting()
    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','root','','article_spider',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql ="""
        insert into jobbole_article(title,url,create_date,fav_nums,comment_nums,praise_nums,content,tags,url_object_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums'],item['comment_nums'],item['praise_nums'],item['content'],item['tags'],item['url_object_id']))

        self.conn.commit()

class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
            self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
                host = settings['MYSQL_HOST'],
                db = settings['MYSQL_DBNAME'],
                user = settings['MYSQL_USER'],
                passwd = settings['MYSQL_PASSWORD'],
                charset ='utf8',
                cursorclass =MySQLdb.cursors.DictCursor,
                use_unicode =True,
             )
        dbpool= adbapi.ConnectionPool('MySQLdb',**dbparms)
        return  cls(dbpool)

    def process_item(self, item, spider):
        query= self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        print(failure)

    def do_insert(self,cursor,item):
        # insert_sql = """
        #               insert into jobbole_article(title,url,create_date,fav_nums,comment_nums,praise_nums,content,tags,url_object_id)
        #               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        #               """
        # cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['fav_nums'], item['comment_nums'],item['praise_nums'], item['content'], item['tags'], item['url_object_id']))

        insert_sql,params=item.get_insert_sql()
        cursor.execute(insert_sql,params)


class ElasticsearchPipline(object):

    def process_item(self,item,spider):

        # article = ArticcleType()
        # article.title = item['title']
        # article.create_date= item['create_date']
        # article.content = remove_tags(item['content'])
        #
        # article.front_image_url=item["front_image_url"]
        # if "front_image_path" in item:
        #  article.front_image_path=item['front_image_path']
        # article.praise_nums = item["praise_nums"]
        # article.fav_nums= item['fav_nums']
        # article.comment_nums = item["comment_nums"]
        # article.tags=item['tags']
        # article.meta.id = item['url_object_id']
        #
        # article.save()

        item.save_to_es()

        return item


