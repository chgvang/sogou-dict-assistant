#!/usr/bin/env python3
from utils.FileUtils   import FileUtils
from pyquery           import PyQuery
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
    def get(url, stream = False):
        return session.get(url, stream = stream)


    @staticmethod
    def pyquery(url):
        return PyQuery(HttpUtils.get(url).text)


    @staticmethod
    def href(url, relationURL):
        return urljoin(url, relationURL)


    @staticmethod
    def download(url, dest = './'):
        response = HttpUtils.get(url, True)

        filename = None
        match = re.search('filename="(.+)"', response.headers.get('Content-Disposition', ''))
        if match:
            filename = match.group(1).encode('latin1').decode('UTF-8', errors = 'ignore')
        if not filename:
            filename = url.split('/')[-1].split('?')[0]

        with FileUtils.openWriter(FileUtils.relpath(dest, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size = 8192):
                file.write(chunk)
