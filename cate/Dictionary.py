#!/usr/bin/env python3
from cate.Base import Base


class Dictionary(Base):
    def __init__(self, url, name, parent=None):
        super(Dictionary, self).__init__(url, name, parent)
