#!/usr/bin/env python3
from cate.RootCategory import RootCategory


def main(url):
    root = RootCategory(url, 'root')
    root.load()

    futures = root.categories[0].load(loadCallback)
    for future in futures:
        while not future.done():
            pass

    futures = root.categories[0].fetch(fetchCallback)
    for future in futures:
        while not future.done():
            pass


def loadCallback(url, total, namepath, name):
    print(url, total, namepath, name)


def fetchCallback(url, index, total, namepath, name, dictionaries):
    print(url, index, total, namepath, name, dictionaries)


if __name__ == '__main__':
    main('https://pinyin.sogou.com/dict/')
