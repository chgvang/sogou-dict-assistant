#!/usr/bin/env python3
from utils.CallUtils   import CallUtils
from utils.FileUtils   import FileUtils
from utils.ThreadUtils import ThreadUtils


class RootDownloader(object):
    def __init__(self, name, dict, parent = None):
        super(RootDownloader, self).__init__()
        self.name = name
        self.dict = dict
        self.parent = parent


    def namepath(self):
        if self.parent == None:
            return self.name
        else:
            return FileUtils.relpath(self.parent.namepath(), self.name)


class Downloader(RootDownloader):
    def __init__(self, name, dict, parent):
        super(Downloader, self).__init__(name, dict, parent)
        self.reader = None
        self.subDownloaders = None


    # 加载下载器
    def load(self, callback = None):
        futures = []
        futures.append(ThreadUtils.submit(self.pending, callback))

        self.subDownloaders = []
        for dir in FileUtils.subdirs(self.namepath()):
            self.subDownloaders.append(Downloader(dir, self.dict, self))
        [futures.extend(d.load(callback)) for d in self.subDownloaders]
        return futures


    # 加载下载器
    def pending(self, callback):
        dictpath = FileUtils.relpath(self.namepath(), self.dict)
        if FileUtils.exists(dictpath):
            self.reader = FileUtils.openReader(dictpath)
            CallUtils.call(callback, FileUtils.countLines(dictpath))


    # 滚动下载
    def down(self):
        # TODO down
        if self.reader == None:
            pass


    # 释放资源
    def flush(self):
        if self.reader != None:
            FileUtils.close(self.reader)
        [d.flush() for d in self.subDownloaders]


    # 获取下载器列表
    @staticmethod
    def list(name, dict):
        root, downloaders = RootDownloader(name, dict), []
        for dir in FileUtils.subdirs(name):
            downloaders.append(Downloader(dir, dict, root))
        return downloaders
