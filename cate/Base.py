#!/usr/bin/env python3
from utils.FileUtils import FileUtils
from utils.HttpUtils import HttpUtils


class Base(object):
    def __init__(self, url, name, parent = None):
        super(Base, self).__init__()
        self.url = url
        self.name = name
        self.parent = parent


    def href(self, relationURL):
        return HttpUtils.href(self.url, relationURL)


    def namepath(self):
        if self.parent == None:
            return self.name
        else:
            return FileUtils.relpath(self.parent.namepath(), self.name)
