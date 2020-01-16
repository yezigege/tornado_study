from tornado import httpclient, web


class APIError(web.HTTPError):
    """
    自定义API异常
    """
    def __init__(self, status_code=200, *args, **kwargs):
        super(APIError, self).__init__(status_code, *args, **kwargs)
        self.kwargs = kwargs
