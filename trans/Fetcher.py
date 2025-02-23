#!/usr/bin/env python3
from utils.DateUtils   import DateUtils
from utils.FileUtils   import FileUtils
from utils.LockUtils   import LockUtils


class Fetcher(object):
    def __init__(self, name):
        super(Fetcher, self).__init__()
        self.name = name
        self.writers = {}
        self.lockers = {}


    # 识别到所有词库大类
    def loadRoot(self, url, namepath, name):
        if FileUtils.exists(namepath):
            timestr = DateUtils.format('-%Y%m%d%H%M%S')
            FileUtils.rename(namepath, name + timestr)
        FileUtils.mkdir(namepath)


    # 识别到大类下词库分页量
    def loadCategory(self, url, total, namepath, name):
        FileUtils.mkdir(namepath)
        self.writers[namepath] = FileUtils.openWriter(FileUtils.relpath(namepath, self.name))
        self.lockers[namepath] = LockUtils.locker()


    # 识别到词库字典文件
    def fetchCategory(self, url, index, total, namepath, name, dictionaries):
        with self.lockers[namepath]:
            writer = self.writers[namepath]
            for dictionary in dictionaries:
                writer.write('%(url)s\n' % {'url': dictionary.url})


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        FileUtils.closeWriter(*list(self.writers.values()))
