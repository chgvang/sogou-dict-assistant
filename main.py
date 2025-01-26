#!/usr/bin/env python3
from cate.RootCategory import RootCategory
from trans.Fetcher     import Fetcher
from utils.ThreadUtils import ThreadUtils

from rich.progress import BarColumn, Progress, SpinnerColumn, TimeElapsedColumn


def fetch(url, name, dict):
    root, fetcher = RootCategory(url, name), Fetcher(dict)

    with Progress(
        '[green]{task.description}', BarColumn(), SpinnerColumn(finished_text = '[green]✔'),
        '[green]{task.completed}/{task.total}', '⏱', TimeElapsedColumn()
    ) as progress:
        task = progress.add_task('◓ Load categories', total = None)
        futures = root.load(fetcher.loadRoot)
        ThreadUtils.wait4done(futures, lambda: progress.update(task, total = len(root.categories)))

        futures = []
        for index, category in enumerate(root.categories):
            subFutures = category.load(fetcher.loadCategory)
            futures += subFutures
            flag = '┣ ' if index + 1 < len(root.categories) else '┗ '
            subTask = progress.add_task(flag + category.namepath(), total = len(subFutures))
            [f.add_done_callback(lambda f, t = subTask: progress.update(t, advance = 1)) for f in subFutures]
            futures.append(ThreadUtils.call4done(subFutures, lambda: progress.update(task, advance = 1)))
        ThreadUtils.wait4done(futures)

        task = progress.add_task('⚫ Fetch categories', total = len(root.categories))
        futures = []
        for index, category in enumerate(root.categories):
            subFutures = category.fetch(fetcher.fetchCategory)
            futures += subFutures
            flag = '┣ ' if index + 1 < len(root.categories) else '┗ '
            subTask = progress.add_task(flag + category.namepath(), total = len(subFutures))
            [f.add_done_callback(lambda f, t = subTask: progress.update(t, advance = 1)) for f in subFutures]
            futures.append(ThreadUtils.call4done(subFutures, lambda: progress.update(task, advance = 1)))
        ThreadUtils.wait4done(futures)


if __name__ == '__main__':
    fetch('https://pinyin.sogou.com/dict/', 'sogou-dict', 'dict.url')
