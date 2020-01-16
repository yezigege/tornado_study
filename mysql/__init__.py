#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import logging

from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import MYSQL
from mysql.stu import STUModel
from mysql.yezi import YeziModel


def create_session(engine):
    """
    参见: https://www.cnblogs.com/geeklove01/p/8179220.html
    使用scoped_session的目的主要是为了线程安全。
    scoped_session类似单例模式，当我们调用使用的时候，会先在Registry里找找之前是否已经创建session了。
    要是有，就把这个session返回。
    要是没有，就创建新的session，注册到Registry中以便下次返回给调用者。
    这样就实现了这样一个目的：在同一个线程中，call scoped_session 的时候，返回的是同一个对象
    :param engine:
    :return:
    """
    if not engine:
        return None
    session = scoped_session(sessionmaker(bind=engine))
    return session()


class Database(object):

    def __init__(self):
        self.schema = 'mysql://%s:%s@%s:%d/%s?charset=utf8'
        self.session = {
            'm': {},
            's': {}
        }
        self.kwargs = {
            'pool_recycle': 3600,
            'echo': options.debug,
            'echo_pool': options.debug
        }

        self.init_session()
        self.stu = STUModel(self)  # study 数据库类
        self.yezi = YeziModel(self)  # yezi 数据库类

    def _session(self, user, passwd, host, port, db, master=True):
        schema = self.schema % (user, passwd, host, port, db)
        engine = create_engine(schema, **self.kwargs)
        session = create_session(engine)
        print('%s: %s' % ('master' if master else 'slave', schema))
        return session

    def init_session(self):
        # master, slaves, dbs = MYSQL['master'], MYSQL['slaves'], MYSQL['dbs']
        master, dbs = MYSQL['master'], MYSQL['dbs']
        for db in dbs:
            # self.session['s'][db] = []

            session = self._session(master['user'], master['pass'], master['host'], master['port'], db)
            self.session['m'][db] = session

            # for slave in slaves:
            #     session = self._session(slave['user'], slave['pass'], slave['host'], slave['port'], db, master=False)
            #     self.session['s'][db].append(session)

    def get_session(self, db, master=False):
        if not master:
            sessions = self.session['s'][db]
            if len(sessions) > 0:
                session = random.choice(sessions)
                return session
        session = self.session['m'][db]
        return session

    @classmethod
    def instance(cls):
        name = 'singleton'  # 单例
        if not hasattr(cls, name):
            setattr(cls, name, cls())
        return getattr(cls, name)

    def close(self):

        def shut(ins):
            try:
                ins.commit()
            except:
                logging.error('MySQL server has gone away. ignore.')
            finally:
                ins.close()

        for db in MYSQL['dbs']:
            shut(self.session['m'][db])
            # for session in self.session['s'][db]:
            #     shut(session)


# global, called by control
pdb = Database.instance()
