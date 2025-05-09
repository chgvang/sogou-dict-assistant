#!/usr/bin/env python3
import struct

from utils.CallUtils import CallUtils
from utils.FileUtils import FileUtils
from utils.ThreadUtils import ThreadUtils


class RootResolver(object):
    def __init__(self, name, suffix, parent=None):
        super(RootResolver, self).__init__()
        self.name = name
        self.suffix = suffix
        self.parent = parent

    def namepath(self):
        if self.parent is None:
            return self.name
        else:
            return FileUtils.relpath(self.parent.namepath(), self.name)


class Resolver(RootResolver):
    def __init__(self, name, suffix, parent):
        super(Resolver, self).__init__(name, suffix, parent)
        self.cells = None
        self.sub_resolvers = None

    def load(self, callback=None):
        """加载解析器
        :param callback: Callback fn
        :return: futures
        """
        futures = [ThreadUtils.submit(self.open, callback)]

        self.sub_resolvers = []
        for subdir in FileUtils.subdirs(self.namepath()):
            self.sub_resolvers.append(Resolver(subdir, self.suffix, self))
        [futures.extend(r.load(callback)) for r in self.sub_resolvers]
        return futures

    def open(self, callback):
        self.cells = []
        for file in FileUtils.subfiles(self.namepath()):
            if file.endswith(self.suffix):
                self.cells.append(Cell(file, FileUtils.relpath(self.namepath(), file)))
        CallUtils.call(callback, len(self.cells))

    def resolve(self, save_as):
        """滚动解析
        :param save_as: save as suffix
        :return: futures
        """
        futures = []
        [futures.append(ThreadUtils.submit(c.resolve, save_as)) for c in self.cells]
        [futures.extend(r.resolve(save_as)) for r in self.sub_resolvers]
        return futures

    @staticmethod
    def list(name, suffix):
        """获取解析器列表
        :param name: sogou dict workspace name
        :param suffix: sogou dict file suffix
        :return: resolvers
        """
        root, resolvers = RootResolver(name, suffix), []
        for subdir in FileUtils.subdirs(name):
            resolvers.append(Resolver(subdir, suffix, root))
        return resolvers


class Cell(object):
    """搜狗细胞词库保存的是unicode编码文本，每两个字节一个字符（中文汉字或者英文字母），找出每数据段的偏移位置即可。
    1、每数据段的内容如下
     0x00   ~ 0x0c   (0    ~ 12) 固定值'\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00'
     0x130  ~ 0x338  (304  ~ 824) 词库名
     0x338  ~ 0x540  (824  ~ 1344) 词库类型
     0x540  ~ 0xd40  (1344 ~ 3392) 描述信息
     0xd40  ~ 0x1540 (3392 ~ 5440) 词库示例
     0x1540 ~ 0x2628 (5440 ~ 9768) 全局拼音表（其中前4字节固定值为'\x9D\x01\x00\x00'）
     0x2628 ~        (9768 ~ ) 汉语词组表
    2、全局拼音表，格式为(index,length,pinyin)的列表
     index: 两个字节的整数，代表这个拼音的索引
     length: 两个字节的整数，代表这个拼音的字节长度
     pinyin: 当前的拼音，每个字符两个字节，拼音总长为length
    3、汉语词组表，格式为(same,py_tab_len,py_tab,{ch_len,ch,ext_len,ext})的列表
     same: 两个字节的整数，代表同音的汉字词语数量（后面的汉字词语组数量）
     py_tab_len: 两个字节的整数，代表汉字词语的拼音长度
     py_tab: 拼音索引段，每个整数两个字节，每个整数代表一个拼音的索引
     {ch_len,ch,ext_len,ext}: 一共重复same次，代表同音的汉字词语组
       ch_len: 两个字节的整数，代表汉字词语字节数长度
       ch: 汉字词语，每个中文汉字两个字节，汉字总长为ch_len
       ext_len: 两个字节的整数，代表扩展信息的长度
       ext: 扩展信息段，前两个字节是一个整数（代表当前汉字词语的序号）、后八个字节全是0
    """

    def __init__(self, name, path):
        super(Cell, self).__init__()
        self.name = name
        self.path = path
        self.dict_name = None
        self.dict_type = None
        self.dict_desc = None
        self.dict_example = None

    def resolve(self, save_as):
        data = None
        with FileUtils.open_reader(self.path, 'rb') as reader:
            data = reader.read()
        if data[0x00:0x0c] != bytes(map(ord, '\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00')):
            return
        self.dict_name = self.byte2str(data[0x130:0x338])
        self.dict_type = self.byte2str(data[0x338:0x540])
        self.dict_desc = self.byte2str(data[0x540:0xd40])
        self.dict_example = self.byte2str(data[0xd40:0x1540])
        py_tab = self.py_table(data[0x1540:0x2628])
        with FileUtils.open_writer(self.path + save_as) as writer:
            self.chinese(data[0x2628:], py_tab, lambda count, py, ch: writer.write('%(ch)s\n' % {'ch': ch}))

    def chinese(self, data, py_tab, fn):
        pos, length = 0, len(data)
        while pos < length:
            # 同音词数量
            same = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            # 拼音索引表长度
            py_tab_len = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            # 拼音索引表
            py = self.py_word(data[pos:pos + py_tab_len], py_tab)
            pos += py_tab_len
            # 中文词组
            for i in range(same):
                # 中文词组长度
                ch_len = struct.unpack('H', data[pos:pos + 2])[0]
                pos += 2
                # 中文词组
                ch = self.byte2str(data[pos:pos + ch_len])
                pos += ch_len
                # 扩展数据长度
                ext_len = struct.unpack('H', data[pos:pos + 2])[0]
                pos += 2
                # 词频
                count = struct.unpack('H', data[pos:pos + 2])[0]
                # 到下个词的偏移位置
                pos += ext_len
                CallUtils.call(fn, count, py, ch)

    def py_word(self, data, py_tab):
        pos, length, string = 0, len(data), ''
        while pos < length:
            index = struct.unpack('H', data[pos:pos + 2])[0]
            string += py_tab[index]
            pos += 2
        return string

    def py_table(self, data):
        if data[0x00:0x04] != bytes(map(ord, '\x9D\x01\x00\x00')):
            return None
        data = data[0x04:]
        pos, length, py_tab = 0, len(data), {}
        while pos < length:
            index = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            l = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            py_tab[index] = self.byte2str(data[pos:pos + l])
            pos += l
        return py_tab

    def byte2str(self, data):
        index, length, string = 0, len(data), ''
        while index < length:
            char = chr(struct.unpack('H', data[index:index + 2])[0])
            if char == '\r':
                string += '\n'
            elif char != ' ':
                string += char
            index += 2
        return string
