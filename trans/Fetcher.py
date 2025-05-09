#!/usr/bin/env python3
from utils.DateUtils import DateUtils
from utils.FileUtils import FileUtils
from utils.LockUtils import LockUtils


class Fetcher(object):
    def __init__(self, dict_url):
        super(Fetcher, self).__init__()
        self.dict_url = dict_url
        self.writers = {}
        self.lockers = {}

    def on_root_loaded(self, root):
        """识别到所有词库大类
        :param root: RootCategory
        """
        name, namepath = root.name, root.namepath()
        if FileUtils.exists(namepath):
            bak_suffix = DateUtils.format('-%Y%m%d%H%M%S')
            FileUtils.rename(namepath, name + bak_suffix)
        FileUtils.mkdir(namepath)

    def on_category_loaded(self, category):
        """识别到大类下词库分页量
        :param category: Category
        """
        namepath = category.namepath()
        FileUtils.mkdir(namepath)
        self.writers[namepath] = FileUtils.open_writer(FileUtils.relpath(namepath, self.dict_url))
        self.lockers[namepath] = LockUtils.locker()

    def on_category_fetched(self, category, dictionaries):
        """识别到词库字典文件
        :param category: Category
        :param dictionaries: Dictionary download urls
        """
        namepath = category.namepath()
        with self.lockers[namepath]:
            writer = self.writers[namepath]
            [writer.write('%(url)s\n' % {'url': d.url}) for d in dictionaries]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        FileUtils.close_writer(*list(self.writers.values()))
