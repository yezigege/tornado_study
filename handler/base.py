#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import logging
import traceback
import datetime
import time

from decimal import Decimal
from tornado import web
from control import ctrl
from settings import ERR
from lib import utils
from tornado.options import options
# from raven.contrib.tornado import SentryMixin
from settings import GZH

from tornado.options import options

# ROOM_API_URL = 'https://coupon.ktvsky.com'


# def get_user_room_by_redis(unionid):
#     room = {}
#     room_id = ctrl.vod_new.get_user_bind_roomid_ctl(unionid)
#     if room_id:
#         room = ctrl.vod_new.get_room_ctl(room_id)
#         room['room_id'] = room_id
#     room['errcode'] = 200
#     return room


def call_limit(key, ex):
    """
    接口调用限制
    :param key:
    :param ex:
    :return:
    """
    try:
        assert ctrl.rs.set(key, 1, ex=ex, nx=True)
    except:
        raise utils.APIError(errcode=10002, errmsg='请勿频繁点击')


# async def get_bind_room_info(unionid):
#     """
#     获取绑定包房基本信息
#     :param unionid:
#     :return:
#     """
#     if options.debug:
#         room = await get_user_room_by_online(unionid)
#     else:
#         room = get_user_room_by_redis(unionid)
#     try:
#         assert room['room_ip'] and room['room_info'] and room['ktvid']
#     except:
#         return
#     return room


# async def get_room_info(room_id):
#     """
#     获取包房信息
#     :param room_id:
#     :return:
#     """
#     url = ROOM_API_URL + '/vadd/room/byid'
#     room = await utilsv2.http_get_async(url, dict(room_id=room_id))
#     try:
#         assert room['room_ip'] and room['room_info'] and room['ktvid']
#     except:
#         raise utils.APIError(errcode=10003, errmsg='not bind room')
#     return room


# class BaseHandler(web.RequestHandler, SentryMixin):
class BaseHandler(web.RequestHandler):

    # 正则表达式对象模板  re.I 不区分大小写
    MOBILE_PATTERN = re.compile('(Mobile|iPod|iPhone|Android|Opera Mini|BlackBerry|webOS|UCWEB|Blazer|PSP)', re.I)

    def _d(self):
        user_agent = self.request.headers.get('user-agent', '').split(';')
        if 'thunder' in user_agent[-1]:
            return 'pc'
        if self.MOBILE_PATTERN.search(self.request.headers.get('user-agent', '')):
            return 'mobile'
        else:
            return 'pc'

    def initialize(self):
        ctrl.pdb.close()

    def on_finish(self):
        ctrl.pdb.close()

    def json_format(self, obj):
        if isinstance(obj, datetime.datetime):  # 判断obj是否是 datetime.datetime 类型
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):  # 判断obj是否是 Decimal 类型  有道云已记
            return ('%.2f' % obj)
        if isinstance(obj, bytes):  # 判断是否是字节类型
            return obj.decode()

    def has_argument(self, name):
        return name in self.request.arguments

    def send_json(self, data=None, errcode=200, errmsg='', status_code=200):
        if data is None:
            data = {}
        res = {
            'errcode': errcode,
            'errmsg': errmsg if errmsg else ERR[errcode]
        }
        res.update(data)

        # if errcode > 200:
        #     logging.error(res)

        json_str = json.dumps(res, default=self.json_format)  # 此处default是自定义json.dumps()转化方法
        if options.debug:  # 如果是 debug 调试模式，则打印相关日志
            logging.info('%s, path: %s, arguments: %s, body: %s, cookies: %s, response: %s'
                         % (
                             self.request.method,
                             self.request.path,
                             self.request.arguments,
                             self.request.body,
                             self.request.cookies,
                             json_str)
                         )

        jsonp = self.get_argument('jsonp', '')
        if jsonp:
            jsonp = re.sub(r'[^\w\.]', '', jsonp)
            self.set_header('Content-Type', 'text/javascript; charet=UTF-8')
            json_str = '%s(%s)' % (jsonp, json_str)
        else:
            self.set_header('Content-Type', 'application/json')

        origin = self.request.headers.get("Origin")
        origin = '*' if not origin else origin
        if self.request.path in ('/common/order', '/upyun/getfile', '/upyun/getfile/info', '/erp/ktv/commonapi', '/wx/share/config'):
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.set_header('Access-Control-Allow-Methods', 'GET')

        if options.debug:
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.set_header('Access-Control-Allow-Methods', '*')

        origin = self.request.headers.get("Origin")
        origin = '*' if not origin else origin
        self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PUT, DELETE')

        if errcode != 200 and self.request.path.startswith('/by/top'):
            status_code = 500
        self.set_status(status_code)  # 本项目所有返回其实都是200。真正的自定义返回码以 josn 方式放在返回数据中。
        self.write(json_str)
        self.finish()

    def dict_args(self):
        _rq_args = self.request.arguments
        rq_args = dict([(k, _rq_args[k][0]) for k in _rq_args])
        return rq_args

    # def _full_url(self):
    #     try:
    #         return self.full_url
    #     except:
    #         return self.request.full_url()

    def render2(self, *args, **kwargs):
        if self.get_argument('json', ''):
            kwargs.pop('config', '')
            self.send_json(kwargs)
            return

        self.render(*args, **kwargs)

    def render_empty(self):
        self.render('error.html', err_title='抱歉，出错了', err_info='抱歉，出错了')

    # def write_error(self, status_code=200, **kwargs):
    #     if 'exc_info' in kwargs:
    #         err_object = kwargs['exc_info'][1]
    #         traceback.format_exception(*kwargs['exc_info'])
    #
    #         if isinstance(err_object, utils.APIError):
    #             err_info = err_object.kwargs
    #             self.send_json(**err_info)
    #             return
    #     if not options.debug:
    #         self.render_empty()
    #     self.captureException(**kwargs)

    def render(self, template_name, **kwargs):
        tp = self.get_argument('tp', '')
        if tp=='out':
            kwargs.update({'show_menu': 1, 'tp': 'out'})
        else:
            kwargs.update({'show_menu': 0, 'tp': tp})

        if options.debug:
            logging.info('render args: %s' % kwargs)
        return super(BaseHandler, self).render(template_name, **kwargs)

    # def log_sentry(self, data):
    #     self.captureMessage(data, stack=True)

    def get_real_ip(self):
        req_headers = self.request.headers
        real_ip = ''
        try:
            if 'X-Forwarded-For' in req_headers:
                real_ip = req_headers['X-Forwarded-For']
            if not real_ip and 'X-Real-Ip' in req_headers:
                real_ip = req_headers['X-Real-Ip']
            if not real_ip:
                real_ip = self.request.remote_ip
        except:
            real_ip = ''
        if real_ip.count(',') > 0:
            real_ip = re.sub(',.*', '', real_ip).strip()
        return real_ip
