#!/usr/bin/env python3
from cate.RootCategory import RootCategory
from trans.Fetcher     import Fetcher
from utils.ThreadUtils import ThreadUtils


fetcher = Fetcher('URL')
def main(url):
    root = RootCategory(url, 'sogou-dict')
    futures = root.load(fetcher.loadRoot)
    ThreadUtils.wait4done(futures)

    futures = root.categories[6].load(fetcher.loadCategory)
    ThreadUtils.wait4done(futures)

    futures = root.categories[6].fetch(fetcher.fetchCategory)
    ThreadUtils.wait4done(futures, fetcher.flush)


if __name__ == '__main__':
    main('https://pinyin.sogou.com/dict/')
