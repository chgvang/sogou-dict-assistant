#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor


threadPoolExecutor = ThreadPoolExecutor(max_workers = 20)


class ThreadUtils(object):
    @staticmethod
    def submit(fn, /, *args, **kvargs):
        return threadPoolExecutor.submit(fn, *args, **kvargs)
