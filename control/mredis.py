#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import datetime
import pickle
import logging

import base64
import random
import string
from hashlib import sha1


class MredisCtrl(object):

    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.stu = ctrl.pdb.stu

    def __getattr__(self, name):
        return getattr(self.api, name)

    def record_index_times(self):
        """记录主页被点击次数"""
        key = "index_times"
        self.ctrl.rs.incr(key)

    def record_mail_times(self):
        """记录邮件发送次数"""
        key = "mail_times"
        self.ctrl.rs.incr(key)

    def record_mail_success_times(self):
        """记录发邮件成功次数"""
        key = "mail_success_times"
        self.ctrl.rs.incr(key)

    def get_record_mail_times(self):
        key = "mail_times"
        return self.ctrl.rs.get(key)

    def get_record_mail_srccess_times(self):
        key = "mail_success_times"
        return self.ctrl.rs.get(key)
