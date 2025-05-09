#!/usr/bin/env python3
from cate.Base import Base
from cate.Category import Category
from cate.CityCategory import CityCategory
from utils.CallUtils import CallUtils
from utils.HttpUtils import HttpUtils
from utils.ThreadUtils import ThreadUtils


class RootCategory(Base):
    def __init__(self, url, name):
        super(RootCategory, self).__init__(url, name)
        self.categories = None

    def load(self, callback=None):
        """加载页面识别所有词库大类
        :param callback: Callback fn
        :return: futures
        """
        return [ThreadUtils.submit(self.pull, callback)]

    def pull(self, callback):
        self.categories = []
        items = HttpUtils.pyquery(self.url).find('#dict_main_3 .dict_category_list_title a').items()
        for item in items:
            url, name = self.href(item.attr('href')), item.text()
            if self.is_city_category(url):
                self.categories.append(CityCategory(url, name, self))
            else:
                self.categories.append(Category(url, name, self))
        CallUtils.call(callback, self)

    def is_city_category(self, url):
        """通过地址识别指定的大类是否为‘城市’大类
        :param url: category url
        :return: boolean
        """
        return url.find('167') != -1
