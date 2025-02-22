#!/usr/bin/env python3
from utils.CallUtils    import CallUtils
from concurrent.futures import ThreadPoolExecutor


threadPoolExecutor = ThreadPoolExecutor(max_workers = 16)


class ThreadUtils(object):
    @staticmethod
    def submit(fn, /, *args, **kvargs):
        return threadPoolExecutor.submit(fn, *args, **kvargs)


    @staticmethod
    def wait4done(futures, callback = None, /, *args, **kvargs):
        for future in futures:
            while not future.done():
                pass
        CallUtils.call(callback, *args, **kvargs)


    @staticmethod
    def call4done(futures, callback, /, *args, **kvargs):
        return ThreadUtils.submit(ThreadUtils.wait4done, futures, callback, *args, **kvargs)
