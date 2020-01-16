"""
测试 asynchttpclient 的使用
"""
import irequest
import logging
import json
from handler.base import BaseHandler


class BaiduHandler(BaseHandler):
    async def get(self):
        url = "https://www.baidu.com"
        v = await irequest.ye.fetch(url, method='GET', connect_timeout=2, request_timeout=2)
        # r = json.loads(bytes(v.body).decode()) if v else {}
        logging.error(v.body)
        print(type(v))
        self.write(v.body.decode())
