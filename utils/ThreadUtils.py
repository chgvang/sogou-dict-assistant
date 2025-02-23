#!/usr/bin/env python3
from utils.CallUtils    import CallUtils
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import threading


threadLocal = threading.local()


class ThreadUtils(object):
    @staticmethod
    def current():
        if not hasattr(threadLocal, 'threadPoolExecutor'):
            threadLocal.threadPoolExecutor = ThreadPoolExecutor(max_workers = 32)
        return threadLocal.threadPoolExecutor


    @staticmethod
    def submit(fn, /, *args, **kvargs):
        return ThreadUtils.current().submit(fn, *args, **kvargs)


    @staticmethod
    def invoke(fn, /, *args, **kvargs):
        future = ThreadUtils.submit(fn, *args, **kvargs)
        wait([future])
        return future.result()


    @staticmethod
    def wait4done(futures, callback = None, /, *args, **kvargs):
        wait(futures)
        CallUtils.call(callback, *args, **kvargs)


    @staticmethod
    def call4done(futures, callback, /, *args, **kvargs):
        return ThreadUtils.submit(ThreadUtils.wait4done, futures, callback, *args, **kvargs)
