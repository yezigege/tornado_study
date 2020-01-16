import logging
from tornado.httpclient import AsyncHTTPClient


class IRequest(object):

    def __init__(self):
        self.cli = AsyncHTTPClient()

    async def fetch(self, url, **kwargs):
        print("启动了此文件。。。")
        try:
            response = await self.cli.fetch(url, **kwargs)
        except Exception as e:
            logging.error('url:%s, error:%s' % (url, e))
        else:
            return response

