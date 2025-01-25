#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from utils.CallUtils    import CallUtils
import threading


threadPoolExecutor = ThreadPoolExecutor(max_workers = 20)


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
    def locker():
        return threading.Lock()
