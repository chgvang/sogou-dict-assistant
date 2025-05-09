#!/usr/bin/env python3
from utils.CallUtils import CallUtils
from utils.FileUtils import FileUtils
from utils.HttpUtils import HttpUtils
from utils.ThreadUtils import ThreadUtils


class RootDownloader(object):
    def __init__(self, name, dict_url, parent=None):
        super(RootDownloader, self).__init__()
        self.name = name
        self.dict_url = dict_url
        self.parent = parent

    def namepath(self):
        if self.parent is None:
            return self.name
        else:
            return FileUtils.relpath(self.parent.namepath(), self.name)


class Downloader(RootDownloader):
    def __init__(self, name, dict_url, parent):
        super(Downloader, self).__init__(name, dict_url, parent)
        self.reader = None
        self.sub_downloaders = None

    def load(self, callback=None):
        """加载下载器
        :param callback: Callback fn
        :return: futures
        """
        futures = [ThreadUtils.submit(self.open, callback)]

        self.sub_downloaders = []
        for subdir in FileUtils.subdirs(self.namepath()):
            self.sub_downloaders.append(Downloader(subdir, self.dict_url, self))
        [futures.extend(d.load(callback)) for d in self.sub_downloaders]
        return futures

    def open(self, callback):
        dictpath = FileUtils.relpath(self.namepath(), self.dict_url)
        if FileUtils.exists(dictpath):
            self.reader = FileUtils.open_reader(dictpath)
            CallUtils.call(callback, FileUtils.count_lines(dictpath))

    def download(self):
        """滚动下载
        :return: futures
        """
        futures = []
        if self.reader is not None:
            with self.reader:
                for line in self.reader:
                    futures.append(ThreadUtils.submit(HttpUtils.download, line.strip(), self.namepath()))
        [futures.extend(d.download()) for d in self.sub_downloaders]
        return futures

    @staticmethod
    def list(name, dict_url):
        """获取下载器列表
        :param name: sogou dict workspace name
        :param dict_url: dict urls file name
        :return: downloaders
        """
        root, downloaders = RootDownloader(name, dict_url), []
        for subdir in FileUtils.subdirs(name):
            downloaders.append(Downloader(subdir, dict_url, root))
        return downloaders
