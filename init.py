#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop

from tornado.options import define, options, parse_command_line

# 如果命令行中带有port同名参数则会称为全局tornado.options的属性，若没有则使用define定义。
define('port', default=8011, help='run on this port', type=int)
define('debug', default=True, help='enable debug mode')

options.parse_command_line()  # 方法一
# parse_command_line()  # 方法二
# 两个parse_command_line() 是一样的方法，两种不同的使用方式
# 作用是：转换命令行参数，并将转换后的值对应的设置到全局 options 对象相关的属性上
# 比如：nohup /home/work/.pyenv/versions/3.6/bin/python app.py -port=9520 > nohup.out &
# 此时的 -port=9520 就会覆盖掉指定 define('port', default..) 端口
# 如果使用 -debug=xxx 就会覆盖掉指定 define('debug', default..)
"""
除了 parse_command_line() 之外，还有 parse_config_file。
第二种是通过配置 config 文件来以其作用。如 port = 8000. 实际中大都不使用此方法
详情参见"http://www.python88.cn/book/tornado24/"


当我们在代码中调用parse_command_line()或者parse_config_file()的方法时，
tornado会默认为我们配置标准logging模块，即默认开启了日志功能，并向标准输出（屏幕）打印日志信息。
如果想关闭tornado默认的日志功能，可以在命令行中添加--logging=none 或者在代码中执行如下操作:
options.logging = None
parse_command_line()
"""


import app


def runserver():
    app.run()
    loop = tornado.ioloop.IOLoop.instance()
    loop.start()


if __name__ == '__main__':
    runserver()
