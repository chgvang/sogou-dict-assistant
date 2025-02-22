#!/usr/bin/env python3
import threading


class LockUtils(object):
    @staticmethod
    def locker():
        return threading.Lock()
