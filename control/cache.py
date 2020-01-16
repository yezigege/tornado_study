#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

from settings import REDIS, OTHER_REDIS


def get_redis_client(conf=REDIS):
    print('redis: %s' % conf['host'])
    return redis.StrictRedis(host=conf['host'], port=conf['port'], db=conf.get('db', 0))


base_redis = get_redis_client(REDIS)
other_redis = get_redis_client(OTHER_REDIS)

