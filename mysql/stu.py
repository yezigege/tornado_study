#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import control
from sqlalchemy import Column, text, or_, and_
from sqlalchemy.sql.expression import func, desc
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM, TINYINT, DATETIME, TIMESTAMP, DECIMAL, TEXT

from lib import utils
from settings import DB_STUDY
from mysql.base import NotNullColumn, Base
from lib.decorator import model_to_dict, models_to_list, filter_update_data, tuple_to_dict


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(11), primary_key=True)
    # openid = NotNullColumn(VARCHAR(64), default='')
    # unionid = NotNullColumn(VARCHAR(64), default='')
    # headimgurl = NotNullColumn(VARCHAR(512), default='')
    nickname = NotNullColumn(VARCHAR(128), default='')
    phone_num = NotNullColumn(VARCHAR(11))
    sex = NotNullColumn(TINYINT(1))
    birthday = NotNullColumn(DATETIME)
    addr = NotNullColumn(VARCHAR(512), default='')


class STUModel(object):

    def __init__(self, pdb):
        self.pdb = pdb
        self.master = pdb.get_session(DB_STUDY, master=True)
        # self.slave = pdb.get_session(DB_STUDY)


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
            raise utils.APIError(400, log_message='添加失败，已经回滚')

    def add_user(self, **kwargs):
        return self.add_table('User', **kwargs)

    def update_user(self, id, data):
        self.master.query(User).filter_by(id=id).update(data)
        self.master.commit()



