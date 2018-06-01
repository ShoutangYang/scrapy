# -*- coding:utf-8 -*-
__author__ = 'Tony.Yang'

import requests
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

agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36'
header ={
    'Host':'www.zhihu.com',
    'Referer':'https://www.zhihu.com/',
    'User-Agent':agent,
    'authorization':'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
    'Connection':'keep-alive',

}

"""
伪造 请求header
"""
session = requests.session()
def get_xsrf():
    response = requests.get("https://www.zhihu.com",headers =header,verify = False)
    print(response.text)
    text ='<input type="hidden" name="_xsrf" value="ca70366e5de5d133c3ae09fb16d9b0fa"/>'
    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text)
    if match_obj:
        print(match_obj.group(1))
        return  match_obj.group(1)
    else:
        return ''
    print(response.text)
    pass

def get_signature(time_str):
    h =hmac.new(key='d1b964811afb40118a12068ff74a12f4'.encode('utf-8'),digestmod=sha1)
    print(h)
    grant_type = 'password'
    client_id='c3cef7c66a1843f8b3a9e6a1e3160e20'
    source='com.zhihu.web'
    now = time_str
    h.update((grant_type+client_id+source+now).encode('utf-8'))
    return h.hexdigest()



def get_xsrf_dc0():
    response = session.get('https://www.zhihu.com/signup',headers=header,verify=False)
    return  response.cookies["_xsrf"],response.cookies['d_c0']


def get_identify(headers):
    response = session.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',headers=headers,verify=False)
    r = re.findall('"show_captcha":(\w+)',response.text)
    if r[0]=='false':
        return ''
    else:
        response =  response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',headers=headers,verify=False)
        show_captcha = json.load(response.text)['img_base64']
        with open('captcha.jpg','wb') as f:
            f.write(base64.b64decode(show_captcha))

        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha = input('输入验证码:')
        session.post('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=header,verify=False,
                     data={"input_text": captcha})
        print(captcha)
        return captcha


def zhihu_login(account, password):
        '''知乎登陆'''
        post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        XXsrftoken, XUDID = get_xsrf_dc0()
        header.update({
            "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",  # 固定值
            "X-Xsrftoken": XXsrftoken,
        })
        time_str = str(int((time.time() * 1000)))
        # 直接写在引号内的值为固定值，
        # 只要知乎不改版反爬虫措施，这些值都不湖边
        post_data = {
            "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
            "grant_type": "password",
            "timestamp": time_str,
            "source": "com.zhihu.web",
            "password": password,
            "username": account,
            "captcha": "",
            "lang": "en",
            "ref_source": "homepage",
            "utm_source": "",
            "signature": get_signature(time_str),
            'captcha': get_identify(header)
        }

        response = session.post(post_url, data=post_data, headers=header, cookies=session.cookies,verify=False)
        if response.status_code == 201:
            # 保存cookie，下次直接读取保存的cookie，不用再次登录

            pass
        else:
            print("登录失败")

def is_login():
    # 通过个人中心页面返回状态码来判断是否登录
    # 通过allow_redirects 设置为不获取重定向后的页面
    response = session.get("https://www.zhihu.com/inbox", headers=header, allow_redirects=False,verify =False)
    if response.status_code != 200:
        zhihu_login("+8618616741206", "360360")
    else:
        print("你已经登陆了")


if __name__ == '__main__':
    # time_str = str(int((time.time()*1000)))
    # print(get_xsrf_dc0())
    # print(get_signature(time_str))
    is_login()