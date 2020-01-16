# redis 配置
REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
}


OTHER_REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 1
}

# mysql 配置
DB_STUDY = 'study'
DB_YEZI = 'yezi'

MYSQL = {
    'master': {
        'host': '127.0.0.1',
        'user': 'root',
        'pass': 'mysql',
        'port': 3306
    },
    # 'slaves': [
    #     {
    #         'host': '10.10.168.41',
    #         'user': 'ktvsky',
    #         'pass': '098f6bcd4621d373cade4e832627b4f7',
    #         'port': 3308
    #     }
    # ],
    DB_YEZI: {
        'master': {
            'host': '127.0.0.1',
            'user': 'root',
            'pass': 'mysql',
            'port': 3306
        },
        # 'slaves': [
        #     {
        #         'host': '10.10.168.41',
        #         'user': 'ktvsky',
        #         'pass': '098f6bcd4621d373cade4e832627b4f7',
        #         'port': 3308
        #     }
        # ],
    },
    'dbs': [DB_STUDY, DB_YEZI]
}


WX_GRANT_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}&connect_redirect=1#wechat_redirect'
WX_USERINFO_GRANT_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo&state={state}&connect_redirect=1#wechat_redirect'
WX_BASE_GRANT_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state={state}&connect_redirect=1#wechat_redirect'
FETCH_OPENID_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
FETCH_WX_USERINFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={access_token}&openid={openid}&lang=zh_CN'
ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
WX_REDIRECT_URL = 'http://wx.handle.ktvdaren.com/coupon/wx'
WX_REDIRECT_COUPON_ORDER_URL = 'http://wx.handle.ktvdaren.com/coupon/order/wx'
WX_MINIAPP_LOGIN_URL = 'https://api.weixin.qq.com/sns/jscode2session'
SONG_ORDER_URL = 'http://k.ktvsky.com/bar/u/remote_ctrl/song/list'
QINIU_DOUMAIN = 'https://qncweb.ktvsky.com/'


# 雷石k歌公众号
LSKG_CONF = {
    'appid': 'wx25d410fd34548b97',
    'appsecret': '151499864564d8112f8323a94d3c94b0',
    'originid': 'gh_9ed59de385fe',
    'order_tpid': 'k1gWnFe1vVIKNrDUAXi0E2OvyPOfCdzGQXnUodz3DAg',
    'buy_card_tpid': 'U7gRlLTZsEiYQiY728Zokrji8w14AujB0lp8RXbhuNM',
    'recharge_card_tpid': 'MzV_do5oKyeu2Mik5Rs5FAUuwcCovYk-JN3hKcpDWbs',
    'card_consumption_tpid': '3Sgx2liAtWhwv_cPsAt8se8QB7BQfyPOlPRDFddKz_4',
}

# 授权主体公众号
WX_CONF = LSKG_CONF

ALI_GRANT_URL = "https://openauth.alipay.com/oauth2/publicAppAuthorize.htm?app_id={appid}&scope=auth_userinfo&redirect_uri={redirect_uri}&state={state}"

ALICONF = {
    'APPID': '2016051601406786',
    'GATEWAY': 'https://openapi.alipay.com/gateway.do',
    'AUTH_URL': 'http://coupon.ktvsky.com/ali/auth/cb',
}

# time
LOCK_TIME = 10
A_HOUR = 3600
A_DAY = 24 * A_HOUR
A_MONTH = 30 * A_DAY
THREE_MON = 90 * A_DAY
TEN_MIN = 600

API_ACCESS_TOKENS = {
    'ktv_steward': '8w4hjtjesld7z9fxz5x92i117kjlz1t8'
}

# error msg
ERR = {
    200: '请求成功',
    # 10000: '应用上线前请使用测试环境进行开发联调',
    10001: '请求参数错误',
    # 10002: '需等上一笔提现打款',
    # 10003: '验证码错误',
    # 10004: 'ktv已被其他代理商激活',
    # 10005: '您没有抽奖机会',
    # 10006: '活动没有在进行中',
    # 11001: '优惠券经验证, 无法使用',
    # 11002: '使用优惠券失败',
    # 12001: '验证码调用次数过多，请明天再试',
    # 19002: '房型已售空',
    # 19003: '支付失败，稍后再试',
    # 19004: '查单失败，稍后再试',
    # 19005: '未登录',
    # 19006: '酒水下单失败, 请检查房台名是否正确',
    # 19007: '红包发放失败',
    # 19008: JOB_IDS'正在开台中，请稍后刷新页面',
    # 18001: '美女包养失败',
    # 40001: '请先在发布平台配置ktv',
    # 40002: '操作不合法，购买/领取数量超过剩余数量',
    # 40003: '频率过高',
    # 40004: '余额不足',
    # 40005: '您不是主宰',
    # 40006: '地址已过期',
    # 40007: '法官已经被别人抢走',
    # 50000: '暂时无法获取到歌厅数据，请稍后再试',
    # 50001: '开放平台服务异常，请稍后再试',
    # 50002: '歌厅房间不可用，请稍后再试',
    # 50003: '该订单已被使用',
    # 50004: '歌厅网络预订接口未授权',
    # 50005: '歌厅此功能被禁用',
    # 50006: '访问频率过高',
    # 50007: '产品列表拉取失败',
    13001: '邮件发送失败，连接失败',
    13002: '邮件发送失败，认证错误',
    13003: '邮件发送失败，发件人被拒绝',
    13004: '邮件发送失败，收件人被拒绝',
    13005: '邮件发送失败，数据接收拒绝',
    13006: '邮件发送失败',
    13007: '邮件发送异常',
}

GZH = {
    'appid': WX_CONF['appid'],
    'appsecret': WX_CONF['appsecret'],
}

# 定时任务id
JOB_IDS = []
