#!/usr/bin/env python
# encoding: utf-8


"""
@version: v0.1
@author: phpergao
@license: Apache Licence 
@contact: endoffight@gmail.com
@site: http://www.phpgao.com
@software: PyCharm
@file: fetion.py
@time: 15-1-27 下午8:55
python调用飞信发送短信
"""

import urllib2
import urllib
import cookielib
import re


class FetionError(Exception):
    def __init__(self, code=0):
        self.code = code

    def __str__(self):
        errors = {
            0: 'Unknown error',
            404: 'Wrong mobile number',
            301: 'Login error',
            403: 'Get token error',
            400: 'Error happens while requesting',
            401: 'Error happens while sending to myself',
            402: 'Error happens while sending to others'
        }
        return errors[self.code]


class Fetion():
    def __init__(self, mob, password, debug=False):
        self.base_url = 'http://f.10086.cn'
        self.mob = mob
        self.password = password
        self.cookie = ''
        self.debug = debug
        self.do_login()

    def __getattr__(self, attr):
        urls = {
            'login_url': '/huc/user/space/login.do',
            'check_login_url': '/im/login/cklogin.action',
            'send_to_me_url': '/im/user/sendMsgToMyselfs.action',
            'send_to_other_url': '/im/chat/sendMsg.action?touserid=',
            'get_uid_url': '/im/index/searchOtherInfoList.action',
            'csrftoken_url': '/im/chat/toinputMsg.action?touserid=',
        }
        return urls[attr]

    def do_login(self):
        post_data = {
            'mobilenum': self.mob,
            'password': self.password,
            "m": "submit",
            "fr": "space",
            "backurl": "http://f.10086.cn/"
        }
        self.send(self.login_url, post_data)
        self.do_check_login()

    def do_check_login(self):
        self.send(self.check_login_url)

    def send_msg(self, mob, msg):
        if mob == self.mob:
            return self.send_to_myself(msg)
        else:
            return self.send_to_other(mob, msg)

    def send_to_myself(self, msg):
        msg = {'msg': msg}
        xml = self.send(self.send_to_me_url, msg)
        if re.search(r'(短信发送成功)', xml) is None:
            raise FetionError(401)
        return True

    def send_to_other(self, mob, msg):
        uid = self.get_uid(mob)
        csrf_token = self.getcsrftoken(uid)
        uri = self.send_to_other_url + uid
        msg = {'msg': msg, 'csrfToken': csrf_token}
        xml = self.send(uri, msg)
        if re.search(r'(发送消息成功)', xml) is None:
            raise FetionError(402)
        return True

    def get_uid(self, mob):
        data = {'searchText': mob}
        xml = self.send(self.get_uid_url, data)
        match = re.search(r'toinputMsg\.action\?touserid=(?P<uid>\d+)', xml)
        if match:
            return match.group('uid')
        else:
            raise FetionError(404)

    def getcsrftoken(self, uid):
        uri = self.csrftoken_url + uid
        xml = self.send(uri)
        match = re.search(r'name="csrfToken"\svalue="(?P<token>\w+)"', xml, re.M)
        if match:
            return match.group('token')
        else:
            raise FetionError(403)

    def send(self, uri, data=''):
        url = self.base_url + str(uri)
        req = urllib2.Request(url)
        # cookie enabled
        if self.cookie == '':
            self.cookie = cookielib.CookieJar()

        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie)

        if self.debug:
            http_handler = urllib2.HTTPHandler(debuglevel=1)
            opener = urllib2.build_opener(cookie_handler, http_handler)
        else:
            opener = urllib2.build_opener(cookie_handler)

        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Cache-Control', 'no-cache')
        req.add_header('Accept', '*/*')
        req.add_header('Connection', 'close')
        # post data
        if data:
            post_data = urllib.urlencode(data)
            req.add_data(post_data)
            req.add_header('Content-Length', len(post_data))
        try:
            response = opener.open(req)
        except urllib2.URLError, error:
            raise FetionError(400)
            exit()
        return response.read()


if __name__ == '__main__':

    yourmob = "136XXXXXXXX"
    password = '123456'

    send_to = '138XXXXXXXX'
    message = '测试短信，请无视'

    m = Fetion(yourmob, password)
    try:
        print m.send_msg(send_to, message)
    except FetionError, e:
        print e