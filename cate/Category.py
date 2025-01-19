#!/usr/bin/env python3
from cate.Base        import Base
from cate.Dictionary  import Dictionary
from utils.HttpUtils  import HttpUtils
from utils.Pagination import Pagination


class Category(Base):
    def __init__(self, url, name, parent = None):
        super(Category, self).__init__(url, name)
        self.parent = parent
        self.pagination = None
        self.dictionaries = None
        self.fetchPageStats = None


    # 解析页面识别大类下词库分页量
    def load(self):
        self.pagination = Pagination(self.url)
        self.pagination.load()
        self.dictionaries = []
        self.fetchPageStats = [False] * self.pagination.total


    # 滚动分页处理大类下的词库列表
    def fetch(self):
        self.pagination.stream(self.resolve)


    # 解析页面识别词库字典文件
    def resolve(self, url, index, total):
        page = HttpUtils.pyquery(url)
        items = page.find('#dict_detail_list .dict_detail_block').items()
        for item in items:
            url = item.find('.dict_dl_btn a').attr('href')
            name = item.find('.detail_title a').text()
            self.dictionaries.append(Dictionary(url, name))
        self.fetchPageStats[index - 1] = True
