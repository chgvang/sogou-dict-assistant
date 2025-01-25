#!/usr/bin/env python3
from utils.HttpUtils import HttpUtils


class Pagination(object):
    def __init__(self, url, total, prefix = None):
        super(Pagination, self).__init__()
        self.url = url
        self.index = 0
        self.total = total
        self.prefix = prefix


    def hasNext(self):
        return self.index < self.total


    def tryNext(self):
        if self.hasNext():
            self.index += 1
            self.url = self.url if self.index == 1 else HttpUtils.href(self.url, self.prefix + str(self.index))
            return True
        return False


    def stream(self, callback, /, *args, **kvargs):
        results = []
        while self.tryNext():
            pageArgs = (self.url, self.index, self.total)
            results.append(callback(*args + pageArgs, **kvargs))
        return results
