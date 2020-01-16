from tornado import web
from control import ctrl
from handler.base import BaseHandler
from lib import utils


class MainHandler(BaseHandler):

    async def get(self):
        """
        注解：这里的ctrl是封装完成的包，ctrl.mredis即是ctrl包下 __init__初始化中的一个对象属性
        :return:
        """
        ctrl.mredis.record_index_times_ctl()  # 记录主页点开次数
        self.write("Hello, world")

    async def post(self):
        """
        添加用户
        :return:
        """
        try:
            nickname = self.get_argument('nickname')
            phone_num = self.get_argument('phone')
            sex = self.get_argument('gender', default='1')  # 默认为 1: 男,  0: 女
            birthday = self.get_argument('birthday')
            addr = self.get_argument('addr')
        except:
            raise utils.APIError(10001)

        ctrl.mredis.add_user(  # 因为add_user 使用了 ** ,所以此处可以使用 xx=xx 的形式
            nickname=nickname,
            phone_num=phone_num,
            sex=sex,
            birthday=birthday,
            addr=addr
        )
