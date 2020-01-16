#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime

from sqlalchemy import Column, text
from sqlalchemy.sql.expression import func, desc, distinct, or_, and_
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM, TINYINT, DATETIME, TIMESTAMP, DOUBLE

from lib import utils
from settings import DB_YEZI
from mysql.base import NotNullColumn, Base
from lib.decorator import datetime_to_str, model_to_dict, models_to_list, filter_update_data


# class GzhList(Base):
#     __tablename__ = 'gzh_list'
#     id = Column(INTEGER(11), primary_key=True)
#     appid = NotNullColumn(VARCHAR(32))
#     appsecret = NotNullColumn(VARCHAR(64))
#     originid = NotNullColumn(VARCHAR(32))
#     qr = NotNullColumn(VARCHAR(128))
#     tag = NotNullColumn(VARCHAR(32))
#     sub_tag = NotNullColumn(VARCHAR(1024))
#     subscribe_num = NotNullColumn(INTEGER(11))
#     state = NotNullColumn(TINYINT(1))
#     weight = NotNullColumn(INTEGER(11))
#     type = NotNullColumn(TINYINT(1))
#     company = NotNullColumn(TINYINT(1))
#     owner = NotNullColumn(TINYINT(1), default=0)  # 公众号所有者（0为自有，1为合作）
#     level = NotNullColumn(TINYINT(1), default=0)  # 设置主吸辅吸（0为主吸，1为辅吸）
#     slowdown = NotNullColumn(TINYINT(1), default=0)  # 是否设为降速（0为否，1为是）
#     pure = NotNullColumn(INTEGER(11), default=0)  # 纯度，即女粉比例（值为0 - 100）
#     start_time = NotNullColumn(DATETIME)  # 上架时间
#     end_time = NotNullColumn(DATETIME)  # 下架时间


class YeziModel(object):

    def __init__(self, pdb):
        self.pdb = pdb
        self.master = pdb.get_session(DB_YEZI, master=True)
        # self.slave = pdb.get_session(DB_YEZI)

    @model_to_dict
    def add_table(self, tb, **kwargs):
        try:
            one = eval(tb)(**kwargs)
            self.master.add(one)
            self.master.commit()
            return one
        except Exception as e:
            logging.error(e)
            self.master.rollback()
            raise utils.APIError(400)
