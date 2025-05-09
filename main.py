#!/usr/bin/env python3
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

from cate.RootCategory import RootCategory
from trans.Downloader import Downloader
from trans.Fetcher import Fetcher
from trans.Resolver import Resolver
from utils.CallUtils import CallUtils
from utils.ThreadUtils import ThreadUtils


def exec_sub_task(progress, task, subs, task_fn):
    tasks, futures = {}, []
    for index, sub in enumerate(subs):
        namepath = sub.namepath()
        # 创建大类的任务进度条
        icon = '┣━' if index + 1 < len(subs) else '┗━'
        sub_task = progress.add_task(icon + namepath, total=None)
        tasks[namepath] = sub_task

    for index, sub in enumerate(subs):
        namepath = sub.namepath()
        sub_task = tasks[namepath]
        # 执行大类任务（返回包含子分类的future列表）
        sub_futures = CallUtils.call(task_fn(sub))
        futures += sub_futures
        # 更新大类总进度数，大类下future完成时更新大类进度，全部完成时更新总进度
        progress.update(sub_task, total=len(sub_futures))
        [f.add_done_callback(lambda f, t=sub_task: progress.update(t, advance=1)) for f in sub_futures]
        futures.append(ThreadUtils.call4done(sub_futures, lambda: progress.update(task, advance=1)))
    ThreadUtils.wait4done(futures, lambda: [progress.update(t, visible=False) for t in tasks.values()])


def fetch(progress, root, fetcher):
    task = progress.add_task('[bold]1/6 Load categories', total=None)
    futures = root.load(fetcher.on_root_loaded)
    ThreadUtils.wait4done(futures, lambda: progress.update(task, total=len(root.categories)))
    exec_sub_task(progress, task, root.categories, lambda c: lambda: ThreadUtils.invoke(c.load, fetcher.on_category_loaded))

    task = progress.add_task('[bold]2/6 Fetch categories', total=len(root.categories))
    exec_sub_task(progress, task, root.categories, lambda c: lambda: ThreadUtils.invoke(c.fetch, fetcher.on_category_fetched))


def download(progress, downloaders):
    task = progress.add_task('[bold]3/6 Load downloader', total=len(downloaders))
    exec_sub_task(progress, task, downloaders, lambda d: lambda: d.load())

    task = progress.add_task('[bold]4/6 Download dictionaries', total=len(downloaders))
    exec_sub_task(progress, task, downloaders, lambda d: lambda: ThreadUtils.invoke(d.download))


def resolve(progress, resolvers, save_as):
    task = progress.add_task('[bold]5/6 Load resolver', total=len(resolvers))
    exec_sub_task(progress, task, resolvers, lambda r: lambda: r.load())

    task = progress.add_task('[bold]6/6 Resolve dictionaries', total=len(resolvers))
    exec_sub_task(progress, task, resolvers, lambda r: lambda: ThreadUtils.invoke(r.resolve, save_as))


if __name__ == '__main__':
    url, name, dict_url, suffix, save_as = 'https://pinyin.sogou.com/dict/', 'sogou-dict', 'dict.url', '.scel', '.txt'

    with Progress(
            '[green][progress.description]{task.description}', BarColumn(),
            SpinnerColumn(finished_text='[green]✔'), MofNCompleteColumn(), '⏱', TimeElapsedColumn()
    ) as progress:
        with Fetcher(dict_url) as fetcher: fetch(progress, RootCategory(url, name), fetcher)
        download(progress, Downloader.list(name, dict_url))
        resolve(progress, Resolver.list(name, suffix), save_as)
