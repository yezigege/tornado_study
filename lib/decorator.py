#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import control
import hashlib
import pickle
import tornado.web

from functools import wraps
from sqlalchemy.orm import class_mapper
from urllib.parse import quote, unquote
from settings import WX_USERINFO_GRANT_URL, WX_CONF, WX_REDIRECT_URL, \
    ALI_GRANT_URL, ALICONF, A_DAY, WX_GRANT_URL,API_ACCESS_TOKENS
from tornado.httputil import url_concat
from tornado.options import options
from lib import utils


def model2dict(model):
    if not model:
        return {}
    fields = class_mapper(model.__class__).columns.keys()
    return dict((col, getattr(model, col)) for col in fields)


def model_to_dict(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return model2dict(ret)
    return wrap


def models_to_list(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [model2dict(r) for r in ret]
    return wrap


def filter_update_data(func):
    def wrap(*args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
            data = dict([(key, value) for key, value in data.items() if value or value == 0])
            kwargs['data'] = data
        return func(*args, **kwargs)
    return wrap


def tuples_first_to_list(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [item[0] for item in ret]
    return wrap


def tuple_to_dict(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [dict(zip(i.keys(), i.values())) for i in ret]
    return wrap


def check_openid_with_scope(scope='snsapi_userinfo'):
    def decorator(func):
        def wrap(*args, **kw):
            # scope = 'snsapi_base'
            self = args[0]
            openid = self.get_cookie('openid')
            if not openid:
                # 去掉一些没用的微信带上来的参数，from=singlemessage, isappinstalled=0/1, 因为state不能长过128
                state = self.request.uri
                if '?' in state:
                    path, params = state.split('?', 1)
                    param_list = params.split('&')
                    param_list = list(filter(lambda x: 'from' not in x and 'isappinstalled' not in x, param_list))
                    state = path+'?'+'&'.join(param_list)

                url = WX_GRANT_URL.format(
                    scope=scope,
                    appid=WX_CONF['appid'],
                    redirect_uri=quote(WX_REDIRECT_URL),
                    state=quote(state)
                )
                # 跳转去授权
                return self.redirect(url)
            return func(*args, **kw)
        return wrap
    return decorator


def check_openid(func):
    @wraps(func)
    def wrap(*args, **kw):
        self = args[0]
        openid = self.get_cookie('openid')
        if not openid:
            # 去掉一些没用的微信带上来的参数，from=singlemessage, isappinstalled=0/1, 因为state不能长过128
            state = self.request.uri
            if self.request.path in ('/ktv/order/namegame'):
                state = '/ktv/order/namegame'
            if '?' in state:
                path, params = state.split('?', 1)
                param_list = params.split('&')
                param_list = list(filter(lambda x: 'from' not in x and 'isappinstalled' not in x, param_list))
                state = path+'?'+'&'.join(param_list)
            url = WX_USERINFO_GRANT_URL.format(
                appid=WX_CONF['appid'],
                redirect_uri=quote(WX_REDIRECT_URL),
                state=quote(state)
            )
            # 跳转去授权
            return self.redirect(url)
        return func(*args, **kw)
    return wrap


def check_alipay_user_id(func):

    def wrap(*args, **kw):
        self = args[0]
        alipay_user_id = self.get_cookie('openid')
        if not alipay_user_id:
            url = ALI_GRANT_URL.format(
                appid=ALICONF['APPID'],
                redirect_uri=quote(ALICONF['AUTH_URL']),
                state=self.request.path
            )
            # 跳转去授权
            return self.redirect(url)
        return func(*args, **kw)
    return wrap


def forbid_frequent_api_call(params={'cookie_keys': [], 'seconds': 1}):
    '''主要是限制前端的点击，所以加了cookie_keys'''
    def decorator(func):
        def wrap(*args, **kw):
            self = args[0]

            arguments = self.request.arguments
            ordered_keys = sorted(arguments.keys())
            ordered_values = [''.join(list(map(bytes.decode, arguments.get(key, '')))) for key in ordered_keys]
            arg_key = ''.join(ordered_values)

            cookie_key = ''
            cookie_keys = params.get('cookie_keys', [])
            if cookie_keys:
                ordered_cookie_keys = sorted(cookie_keys)
                ordered_cookie_values = [str(self.get_cookie(key, '')) for key in ordered_cookie_keys]
                cookie_key = ''.join(ordered_cookie_values)

            key = arg_key + cookie_key
            if control.ctrl.rs.exists(key):
                return self.send_json(dict(errcode=50001, errmsg='操作过于频繁'))
            control.ctrl.rs.set(key, 1, params.get('seconds', 1))
            return func(*args, **kw)
        return wrap
    return decorator


def save_args(func):
    def wrap(*args, **kw):
        ctrl = control.ctrl
        self = args[0]
        self.full_url = self.request.full_url()
        if self.has_argument('args'):
            try:
                # restore args
                key = self.get_argument('args')
                self.request.arguments.update(json.loads(unquote(ctrl.rs.get(key).decode())))
            except:
                pass
        else:
            # save args
            key = 'SSAT' + hashlib.md5(self.request.uri.encode()).hexdigest()
            ctrl.rs.set(key, quote(json.dumps(self.request.arguments, default=self.json_format)), A_DAY*30)
            ctrl.rs.set('uri_%s'%key, quote(self.request.uri), A_DAY)
            self.request.uri = url_concat(self.request.path, dict(args=key))
            self.request.arguments.update(dict(args=[key]))
        return func(*args, **kw)
    return wrap


def cache_func(prefix=''):
    '''对函数结果进行缓存'''
    def decorator(func):
        def wrap(*args, **kw):
            ctrl = control.ctrl
            key = prefix+'_'+func.__name__+'_'.join([str(o) for o in args[1:]])
            if ctrl.rs.exists(key):
                return pickle.loads(ctrl.rs.get(key))
            ret = func(*args, **kw)
            ctrl.rs.set(key, pickle.dumps(ret), A_DAY)
            return ret
        return wrap
    return decorator


def access_authenticated(token_key=''):
    #接口访问权限验证
    def decorator(func):
        def wrap(self,*args, **kw):
            token = self.request.headers.get("Authorization",'')
            if token_key and token!=API_ACCESS_TOKENS[token_key]:
                raise tornado.web.HTTPError(401)
            return func(self,*args, **kw)
        return wrap
    return decorator


def guest_not_allow(func):
    def wrap(*args, **kw):
        self = args[0]
        if not options.debug and self.is_guest():
            raise utils.APIError(errcode=1001, errmsg='无权限操作')
        return func(*args, **kw)
    return wrap


def api_check_login(func):
    def wrap(*args, **kw):
        self = args[0]
        # wow 账号使用
        if self.get_argument('tk', '')=='6faa8040da20ef399b63a72d0e4ab575':
            self.ktv_id = int(self.get_argument('ktv_id', 0))
            self._login(dict(username='wow-test', ktv_id=self.ktv_id))
            return func(*args, **kw)

        is_login = self.get_secure_cookie('is_login')
        if not is_login:
            return self.send_json(dict(errcode=40001, errmsg='not login'))

        self.ktv_id = int(is_login.decode())
        return func(*args, **kw)
    return wrap


def datetime_to_str(func):
    def wraper(*args, **kwargs):
        ret = func(*args, **kwargs)
        for i in ret:
            i['create_time'] = i['create_time'].strftime('%Y/%m/%d %H:%M:%S')
            i['update_time'] = i['update_time'].strftime('%Y/%m/%d %H:%M:%S')
        return ret
    return wraper
