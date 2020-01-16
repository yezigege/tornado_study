#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web
from tornado.options import options


class WeixinConsoleModule(web.UIModule):

    def render(self, force_show=False):
        if options.debug or force_show:
            return self.render_string('ui-mod/vconsole.tpl')
        return ''
