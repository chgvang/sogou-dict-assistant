#!/usr/bin/env python3
from pyquery           import PyQuery
from requests.adapters import HTTPAdapter
from urllib.parse      import urljoin
from urllib3           import Retry
import requests


retryStrategy = Retry(
    total            = 5, # 最大重试次数
    connect          = 3, # 连接重试次数
    read             = 2, # 读取重试次数
    redirect         = 3, # 重定向重试次数
    status_forcelist = [500, 502, 503, 504], # 强制重试状态码
    backoff_factor   = 1, # 等待时间（指数递增：1s、2s、4s）
    raise_on_status  = True # 最大重试次数后是否抛出异常
)


httpAdapter = HTTPAdapter(max_retries = retryStrategy)
session = requests.session()
session.mount('https://', httpAdapter)
session.mount('http://', httpAdapter)


class HttpUtils(object):
    @staticmethod
    def get(url):
        return session.get(url)


    @staticmethod
    def pyquery(url):
        return PyQuery(HttpUtils.get(url).text)


    @staticmethod
    def href(url, relationURL):
        return urljoin(url, relationURL)
