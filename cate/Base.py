#!/usr/bin/env python3
from utils.HttpUtils import HttpUtils


class Base(object):
    def __init__(self, url, name):
        super(Base, self).__init__()
        self.url = url
        self.name = name


    def href(self, relationURL):
        return HttpUtils.href(self.url, relationURL)
