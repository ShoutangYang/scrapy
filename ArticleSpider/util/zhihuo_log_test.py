# -*- coding:utf-8 -*-
__author__ = 'Tony.Yang'


from   selenium import webdriver
from scrapy.selector import Selector
import  datetime
import time
brower = webdriver.Chrome()

brower.get('https://www.zhihu.com/signin')
time .sleep(5)

brower.find_element_by_css_selector('.SignFlow-accountInput input[name="username"]').send_keys('18616741206')
brower.find_element_by_css_selector('.SignFlow-password .Input-wrapper input[name="password"]').send_keys('360360')

brower.find_element_by_css_selector(' button.SignFlow-submitButton').click()
time .sleep(5)
page  = brower.page_source()
print(page)
for i in range(3):
    brower.execute_script('window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;')

brower.quit()