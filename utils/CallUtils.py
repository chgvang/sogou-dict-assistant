#!/usr/bin/env python3


class CallUtils(object):
    @staticmethod
    def call(fn = 'callback', *args, **kvargs):
        if callable(fn):
            fn(*args, **kvargs)
        elif type(fn) == str:
            CallUtils.call(kvargs.pop(fn), *args, **kvargs)
