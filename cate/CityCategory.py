#!/usr/bin/env python3
from cate.Category import Category
from utils.HttpUtils import HttpUtils


class CityCategory(Category):
    def __init__(self, url, name, parent=None):
        super(CityCategory, self).__init__(url, name, parent)
        self.sub_categories = None

    def load(self, callback=None):
        """加载页面识别子类量
        :param callback: Callback fn
        :return: futures
        """
        self.load_sub_category()
        futures = []
        [futures.extend(c.load(callback)) for c in self.sub_categories]
        return futures

    def load_sub_category(self):
        """加载‘城市’大类，识别下级所有的子类
        """
        # 城市大类需通过子类加载，先通过其中一个小类加载识别
        self.sub_categories = []
        page = HttpUtils.pyquery(self.href('360'))
        items = page.find('#city_list_show .city_list a').items()
        for item in items:
            url, name = self.href(item.attr('href')), item.text()
            self.sub_categories.append(Category(url, name, self))

    def fetch(self, callback=None):
        """滚动分页处理大类下的词库列表
        :param callback: Callback fn
        :return: futures
        """
        futures = []
        [futures.extend(c.fetch(callback)) for c in self.sub_categories]
        return futures
