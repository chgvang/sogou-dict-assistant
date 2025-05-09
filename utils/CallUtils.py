#!/usr/bin/env python3


class CallUtils(object):
    @staticmethod
    def call(fn='fn', /, *args, **kwargs):
        if callable(fn):
            return fn(*args, **kwargs)
        elif type(fn) == str:
            return CallUtils.call(kwargs.pop(fn), *args, **kwargs)
        return None
