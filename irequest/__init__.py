from tornado.httpclient import AsyncHTTPClient
from irequest.base import IRequest


# 设置一个异步客户端
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=500)


ye = AsyncHTTPClient()
