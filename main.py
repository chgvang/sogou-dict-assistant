#!/usr/bin/env python3
from cate.RootCategory import RootCategory


def main(url):
    root = RootCategory(url, 'root')
    root.load()

    root.categories[6].load()
    root.categories[6].fetch(fetchCallback)


def fetchCallback(dictionaries, namepath, url, index, total):
    print(dictionaries, namepath, url, index, total)


if __name__ == '__main__':
    main('https://pinyin.sogou.com/dict/')
