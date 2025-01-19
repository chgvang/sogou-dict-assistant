#!/usr/bin/env python3
from cate.Category   import Category
from utils.HttpUtils import HttpUtils


class CityCategory(Category):
    def __init__(self, url, name):
        super(CityCategory, self).__init__(url, name)
        self.subCategories = None


    # 解析页面识别子类量
    def load(self):
        self.fetchSubCategory()
        for category in self.subCategories:
            category.load()


    # 滚动分页处理大类下的词库列表
    def fetch(self):
        for category in self.subCategories:
            category.fetch()


    # 解析‘城市’大类，识别下级所有的子类
    def fetchSubCategory(self):
        # 城市大类需通过子类加载，先通过其中一个小类加载识别
        self.subCategories = []
        page = HttpUtils.pyquery(self.href('360'))
        items = page.find('#city_list_show .city_list a').items()
        for item in items:
            url, name = self.href(item.attr('href')), item.text()
            self.subCategories.append(Category(url, name, self))
