#!/usr/bin/env python3
from pyquery           import PyQuery
from pySmartDL         import SmartDL
from requests.adapters import HTTPAdapter
from urllib.parse      import urljoin
from urllib3           import Retry
import re
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


    @staticmethod
    def downname(url):
        name = None
        match = re.search('filename="(.+)"', requests.get(url, stream = True).headers.get('Content-Disposition', ''))
        if match:
            name = match.group(1).encode('latin1').decode('UTF-8', errors = 'ignore')
        if not name:
            name = url.split('/')[-1].split('?')[0]
        return name


    @staticmethod
    def download(url, dest = './', threads = 16, progress_bar = False, blocking = True):
        dl = SmartDL(url, dest, threads = threads, progress_bar = progress_bar)
        dl.start(blocking = blocking)
        return dl
