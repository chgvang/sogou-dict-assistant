#!/usr/bin/env python3
from cate.RootCategory import RootCategory
from trans.Downloader  import Downloader
from trans.Fetcher     import Fetcher
from utils.ThreadUtils import ThreadUtils

from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn


def fetch(root, fetcher, progress):
    with progress:
        task = progress.add_task('[bold]◓ Load categories', total = None)
        futures = root.load(fetcher.loadRoot)
        ThreadUtils.wait4done(futures, lambda: progress.update(task, total = len(root.categories)))

        futures, subTasks = [], []
        for index, category in enumerate(root.categories):
            # 执行大类任务（返回包含子分类的future列表）
            subFutures = category.load(fetcher.loadCategory)
            futures += subFutures
            # 创建大类的任务进度条
            flag = '┣━' if index + 1 < len(root.categories) else '┗━'
            subTask = progress.add_task(flag + category.namepath(), total = len(subFutures))
            subTasks.append(subTask)
            # 大类的每个future完成时更新大类任务进度条，全部完成时更新总进度条
            [f.add_done_callback(lambda f, t = subTask: progress.update(t, advance = 1)) for f in subFutures]
            futures.append(ThreadUtils.call4done(subFutures, lambda: progress.update(task, advance = 1)))
        ThreadUtils.wait4done(futures, lambda: [progress.update(t, visible = False) for t in subTasks])

        task = progress.add_task('[bold]◒ Fetch categories', total = len(root.categories))
        futures, subTasks = [], []
        for index, category in enumerate(root.categories):
            # 执行大类任务（返回包含子分类的future列表）
            subFutures = category.fetch(fetcher.fetchCategory)
            futures += subFutures
            # 创建大类的任务进度条
            flag = '┣━' if index + 1 < len(root.categories) else '┗━'
            subTask = progress.add_task(flag + category.namepath(), total = len(subFutures))
            subTasks.append(subTask)
            # 大类的每个future完成时更新大类任务进度条，全部完成时更新总进度条
            [f.add_done_callback(lambda f, t = subTask: progress.update(t, advance = 1)) for f in subFutures]
            futures.append(ThreadUtils.call4done(subFutures, lambda: progress.update(task, advance = 1)))
        ThreadUtils.wait4done(futures, lambda: [progress.update(t, visible = False) for t in subTasks])


def download(downloaders, progress):
    with progress:
        totals = {}

        task = progress.add_task('[bold]◓ Load downloader', total = len(downloaders))
        futures, subTasks = [], []
        for index, downloader in enumerate(downloaders):
            namepath = downloader.namepath()
            totals[namepath] = 0
            # 执行大类任务（返回包含子分类的future列表），大类或子分类完成时更新对应的字典数
            subFutures = downloader.load(lambda c, p = namepath: totals.update({p: totals[p] + c}))
            futures += subFutures
            # 创建大类的任务进度条
            flag = '┣━' if index + 1 < len(downloaders) else '┗━'
            subTask = progress.add_task(flag + namepath, total = len(subFutures))
            subTasks.append(subTask)
            # 大类的每个future完成时更新大类任务进度条，全部完成时更新总进度条
            [f.add_done_callback(lambda f, t = subTask: progress.update(t, advance = 1)) for f in subFutures]
            futures.append(ThreadUtils.call4done(subFutures, lambda: progress.update(task, advance = 1)))
        ThreadUtils.wait4done(futures, lambda: [progress.update(t, visible = False) for t in subTasks])

        task = progress.add_task('[bold]◒ Download Dictionaries', total = len(downloaders))
        futures, subTasks = [], []
        for index, downloader in enumerate(downloaders):
            namepath = downloader.namepath()
            # 创建大类的任务进度条
            flag = '┣━' if index + 1 < len(downloaders) else '┗━'
            subTask = progress.add_task(flag + namepath, total = totals[namepath])
            subTasks.append(subTask)
            # TODO down and update progress


if __name__ == '__main__':
    url, name, dict = 'https://pinyin.sogou.com/dict/', 'sogou-dict', 'dict.url'

    progress = Progress(
        '[green][progress.description]{task.description}', BarColumn(),
        SpinnerColumn(finished_text = '[green]✔'), MofNCompleteColumn(), '⏱', TimeElapsedColumn()
    )

    # fetch(RootCategory(url, name), Fetcher(dict), progress)
    download(Downloader.list(name, dict), progress)
