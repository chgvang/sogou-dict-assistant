#!/usr/bin/env python3
import time


class DateUtils(object):
    @staticmethod
    def format(pattern, datetime=None):
        if datetime is None:
            datetime = time.localtime()
        return time.strftime(pattern, datetime)
