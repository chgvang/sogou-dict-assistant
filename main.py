#!/usr/bin/env python3
from cate.RootCategory import RootCategory
from utils.ThreadUtils import ThreadUtils


def main(url):
    root = RootCategory(url, 'sogou-dict')
    root.load()

    futures = root.categories[0].load(loadCallback)
    ThreadUtils.wait4done(futures)

    futures = root.categories[0].fetch(fetchCallback)
    ThreadUtils.wait4done(futures)


def loadCallback(url, total, namepath, name):
    print(url, total, namepath, name)


def fetchCallback(url, index, total, namepath, name, dictionaries):
    print(url, index, total, namepath, name, dictionaries)


if __name__ == '__main__':
    main('https://pinyin.sogou.com/dict/')
