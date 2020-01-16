#!/usr/bin/env python
# -*- coding: utf-8 -*-

from control.mredis import MredisCtrl
from control.cache import base_redis, other_redis
from mysql import pdb


class Ctrl(object):

    def __init__(self):
        self.__method_ren()

        self.pdb = pdb
        self.rs = base_redis
        self.o_rs = other_redis

        # 此处 mredis 是来自 control 包下的 mredis.py 中的 MredisCtrl 对象
        # 这个 MredisCtrl 对象的初始化操作即 __init__() 中有一个默认接收参数
        # 此时这个接受的参数正是这个 Ctrl() 对象本身
        self.mredis = MredisCtrl(self)

    def __method_ren(self):
        """重命名control下的函数名，防止命名冲突"""
        for std in globals():
            if std.find('Ctrl') == -1:
                continue

            cls = globals()[std]
            for func in dir(cls):
                if callable(getattr(cls, func)) and not func.startswith('__'):
                    setattr(cls, '%s_ctl' % func, getattr(cls, func))
                    delattr(cls, func)


# global, called by handler
ctrl = Ctrl()
