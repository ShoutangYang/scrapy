# -*- coding:utf-8 -*-
__author__ = 'Tony.Yang'

from selenium import  webdriver
import  time

if __name__ == '__main__':
    driver  = webdriver.Chrome()
    driver.get('http://www.baidu.com')
    driver.find_element_by_xpath('//*[@id ="kw"]').send_keys('python')
    # //*[@id="kw"]

    time.sleep(20)
    driver.find_element_by_xpath("//*[@id='su']").click()
    print(driver.page_source)
    driver.quit()

