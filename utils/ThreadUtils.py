#!/usr/bin/env python3
import threading
from concurrent.futures import ThreadPoolExecutor, wait

from utils.CallUtils import CallUtils

thread_local = threading.local()


class ThreadUtils(object):
    @staticmethod
    def current():
        if not hasattr(thread_local, 'thread_pool_executor'):
            thread_local.thread_pool_executor = ThreadPoolExecutor(max_workers=16)
        return thread_local.thread_pool_executor

    @staticmethod
    def submit(fn, /, *args, **kwargs):
        return ThreadUtils.current().submit(fn, *args, **kwargs)

    @staticmethod
    def invoke(fn, /, *args, **kwargs):
        future = ThreadUtils.submit(fn, *args, **kwargs)
        wait([future])
        return future.result()

    @staticmethod
    def wait4done(futures, fn=None, /, *args, **kwargs):
        wait(futures)
        CallUtils.call(fn, *args, **kwargs)

    @staticmethod
    def call4done(futures, fn, /, *args, **kwargs):
        return ThreadUtils.submit(ThreadUtils.wait4done, futures, fn, *args, **kwargs)
