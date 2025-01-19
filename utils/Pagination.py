#!/usr/bin/env python3
from utils.HttpUtils import HttpUtils


class Pagination(object):
    def __init__(self, url):
        super(Pagination, self).__init__()
        self.url = url
        self.index = 0
        self.total = 0
        self.prefix = None


    def load(self):
        pages = HttpUtils.pyquery(self.url).find('#dict_page ul li a')

        # 单页场景（不存在分页器）
        if pages.size() == 0:
            self.index = 0
            self.total = 1
            return

        # 多页场景（通过分页器采集分页信息）
        self.index = 0
        self.total = int(pages.eq(-2).text())
        self.prefix = pages.eq(-2).attr('href')[0:-len(str(self.total))]


    def hasNext(self):
        return self.index < self.total


    def tryNext(self):
        if self.hasNext():
            self.index += 1
            self.url = self.url if self.index == 1 else HttpUtils.href(self.url, self.prefix + str(self.index))
            return True
        return False


    def stream(self, callback):
        while self.tryNext():
            callback(self.url, self.index, self.total)
