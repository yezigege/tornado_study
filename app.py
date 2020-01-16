import os
import sys
import uuid
import base64
from tornado.httpserver import HTTPServer

import tornado.ioloop
from tornado import web
from tornado.options import options
from lib import uimodules, uimethods
from apscheduler.schedulers.tornado import TornadoScheduler

scheduler = None
STATIC_PATH = os.path.join(sys.path[0], 'static')  # 添加静态文件位置
TPL_PATH = os.path.join(sys.path[0], 'templates')  # 添加模板文件位置


# 接口地址
URLS = [
    [r'localhost',
        (r'/', 'handler.index.MainHandler'),
        (r'/job', 'handler.scheduler.SchedulerMainHandler'),  # 定时任务测试
        (r'/scheduler', 'handler.scheduler.SchedulerHandler'),
        (r'/mail', 'handler.mail.SendMailHandler'),  # 发送邮件
        (r'/get/baidu', 'handler.asynchttpclient_test.BaiduHandler')  # 异步客户端测试
     ]
]


# 初始化
def init_scheduler():
    global scheduler
    scheduler = TornadoScheduler()
    scheduler.start()
    print('[Scheduler Init]APScheduler has been started')


class Application(web.Application):

    def __init__(self):
        settings = {
            'login_url': '/login',
            'xsrf_cookies': False,  # 开启XSRF保护(跨站请求伪造)
            'compress_response': True,  # 数据压缩
            'debug': options.debug,  # 测试环境
            'ui_modules': uimodules,  # 手机测试环境那个绿色小图标
            'ui_methods': uimethods,  # 自定义方法，数据返回给前端时，模板使用(eg.https://blog.csdn.net/dangsh_/article/details/79315434)
            'static_path': STATIC_PATH,  # 静态文件地址
            'template_path': TPL_PATH,  # 模板文件地址
            'cookie_secret': base64.b64encode(uuid.uuid3(uuid.NAMESPACE_DNS, 'yezi').bytes),  # cookie秘钥
            # 添加 sentry 失败，Docker 下 Sentry 需要 2400MB 运存
        }
        web.Application.__init__(self, **settings)  # 运行上述 settings

        for spec in URLS:
            host = '.*$'  # 点开 add_handlers ，看源码
            handlers = spec[1:]
            # 源码讲解 https://blog.51cto.com/altboy/1958775
            self.add_handlers(host, handlers)


def run():
    # 添加定时任务
    init_scheduler()

    application = Application()
    # 解释来自 https://my.oschina.net/zzir/blog/659688
    # 当运行在一个负载均衡器例如nginx，建议传递xheaders=True 给 HTTPServer 的构造器。
    # 这将告诉Tornado使用类似 X-Real-IP
    # 这样的HTTP头来获取用户的IP地址而不是把所有流量都认为来自于负载均衡器的IP地址。
    # http_server = HTTPServer(application, xheaders=True)

    http_server = HTTPServer(application)
    http_server.listen(options.port)
    print('Running on port %d' % options.port)
