#!/usr/bin/env python3
from cate.Base         import Base
from cate.Dictionary   import Dictionary
from utils.CallUtils   import CallUtils
from utils.HttpUtils   import HttpUtils
from utils.Pagination  import Pagination
from utils.ThreadUtils import ThreadUtils


class Category(Base):
    def __init__(self, url, name, parent = None):
        super(Category, self).__init__(url, name, parent)
        self.pagination = None


    # 解析页面识别大类下词库分页量
    def load(self, callback = None):
        return [ThreadUtils.submit(self.pending, callback)]


    # 解析页面识别分页器
    def pending(self, callback):
        pages = HttpUtils.pyquery(self.url).find('#dict_page ul li a')
        if pages.size() == 0: # 单页场景（不存在分页器）
            self.pagination = Pagination(self.url, 1)
        else: # 多页场景（通过分页器采集分页信息）
            total = int(pages.eq(-2).text())
            prefix = pages.eq(-2).attr('href')[0:-len(str(total))]
            self.pagination = Pagination(self.url, total, prefix)
        CallUtils.call(callback, self.url, self.pagination.total, self.namepath(), self.name)


    # 滚动分页处理大类下的词库列表
    def fetch(self, callback = None):
        return self.pagination.stream(ThreadUtils.submit, self.resolve, callback = callback)


    # 解析页面识别词库字典文件
    def resolve(self, url, index, total, /, *args, **kvargs):
        dictionaries = []
        page = HttpUtils.pyquery(url)
        items = page.find('#dict_detail_list .dict_detail_block').items()
        for item in items:
            uri = item.find('.dict_dl_btn a').attr('href')
            name = item.find('.detail_title a').text()
            dictionaries.append(Dictionary(uri, name))
        CallUtils.call('callback', url, index, total, self.namepath(), self.name, dictionaries, **kvargs)
