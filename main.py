#!/usr/bin/env python3
from cate.RootCategory import RootCategory


def main(url):
    root = RootCategory(url, 'root')
    root.load()


if __name__ == '__main__':
    main('https://pinyin.sogou.com/dict/')
