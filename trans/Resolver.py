#!/usr/bin/env python3
from utils.CallUtils   import CallUtils
from utils.FileUtils   import FileUtils
from utils.ThreadUtils import ThreadUtils
import struct


class RootResolver(object):
    def __init__(self, name, suffix, parent = None):
        super(RootResolver, self).__init__()
        self.name = name
        self.suffix = suffix
        self.parent = parent


    def namepath(self):
        if self.parent == None:
            return self.name
        else:
            return FileUtils.relpath(self.parent.namepath(), self.name)


class Resolver(RootResolver):
    def __init__(self, name, suffix, parent):
        super(Resolver, self).__init__(name, suffix, parent)
        self.cells = None
        self.subResolvers = None


    # 加载解析器
    def load(self, callback = None):
        futures = []
        futures.append(ThreadUtils.submit(self.pending, callback))

        self.subResolvers = []
        for dir in FileUtils.subdirs(self.namepath()):
            self.subResolvers.append(Resolver(dir, self.suffix, self))
        [futures.extend(r.load(callback)) for r in self.subResolvers]
        return futures


    # 加载解析器
    def pending(self, callback):
        self.cells = []
        for file in FileUtils.subfiles(self.namepath()):
            if file.endswith(self.suffix):
                self.cells.append(Cell(file, FileUtils.relpath(self.namepath(), file)))
        CallUtils.call(callback, len(self.cells))


    # 滚动解析
    def resolve(self, saveas):
        futures = []
        [futures.append(ThreadUtils.submit(c.resolve, saveas)) for c in self.cells]
        [futures.extend(r.resolve(saveas)) for r in self.subResolvers]
        return futures


    # 获取解析器列表
    @staticmethod
    def list(name, suffix):
        root, resolvers = RootResolver(name, suffix), []
        for dir in FileUtils.subdirs(name):
            resolvers.append(Resolver(dir, suffix, root))
        return resolvers


# 搜狗细胞词库保存的是unicode编码文本，每两个字节一个字符（中文汉字或者英文字母），找出每数据段的偏移位置即可。
# 1、每数据段的内容如下
#    0x00   ~ 0x0c   (0    ~ 12) 固定值'\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00'
#    0x130  ~ 0x338  (304  ~ 824) 词库名
#    0x338  ~ 0x540  (824  ~ 1344) 词库类型
#    0x540  ~ 0xd40  (1344 ~ 3392) 描述信息
#    0xd40  ~ 0x1540 (3392 ~ 5440) 词库示例
#    0x1540 ~ 0x2628 (5440 ~ 9768) 全局拼音表（其中前4字节固定值为'\x9D\x01\x00\x00'）
#    0x2628 ~        (9768 ~ ) 汉语词组表
# 2、全局拼音表，格式为(index,length,pinyin)的列表
#    index: 两个字节的整数，代表这个拼音的索引
#    length: 两个字节的整数，代表这个拼音的字节长度
#    pinyin: 当前的拼音，每个字符两个字节，拼音总长为length
# 3、汉语词组表，格式为(same,pyTabLen,pyTab,{chLen,ch,extLen,ext})的列表
#    same: 两个字节的整数，代表同音的汉字词语数量（后面的汉字词语组数量）
#    pyTabLen: 两个字节的整数，代表汉字词语的拼音长度
#    pyTab: 拼音索引段，每个整数两个字节，每个整数代表一个拼音的索引
#    {chLen,ch,extLen,ext}: 一共重复same次，代表同音的汉字词语组
#      chLen: 两个字节的整数，代表汉字词语字节数长度
#      ch: 汉字词语，每个中文汉字两个字节，汉字总长为chLen
#      extLen: 两个字节的整数，代表扩展信息的长度
#      ext: 扩展信息段，前两个字节是一个整数（代表当前汉字词语的序号）、后八个字节全是0
class Cell(object):
    def __init__(self, name, path):
        super(Cell, self).__init__()
        self.name = name
        self.path = path
        self.scelName = None
        self.scelType = None
        self.scelDesc = None
        self.scelExample = None


    def resolve(self, saveas):
        data = None
        with FileUtils.openReader(self.path, 'rb') as reader:
            data = reader.read()
        if data[0x00:0x0c] != bytes(map(ord, '\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00')):
            return
        self.scelName = self.byte2str(data[0x130:0x338])
        self.scelType = self.byte2str(data[0x338:0x540])
        self.scelDesc = self.byte2str(data[0x540:0xd40])
        self.scelExample = self.byte2str(data[0xd40:0x1540])
        pyTab = self.pyTable(data[0x1540:0x2628])
        with FileUtils.openWriter(self.path + saveas) as writer:
            self.chinese(data[0x2628:], pyTab, lambda count, py, ch: writer.write('%(ch)s\n' % {'ch': ch}))


    def chinese(self, data, pyTab, callback):
        pos, length = 0, len(data)
        while pos < length:
            # 同音词数量
            same = struct.unpack('H', data[pos:pos+2])[0]
            pos += 2
            # 拼音索引表长度
            pyTabLen = struct.unpack('H', data[pos:pos+2])[0]
            pos += 2
            # 拼音索引表
            py = self.pyWord(data[pos:pos+pyTabLen], pyTab)
            pos += pyTabLen
            # 中文词组
            for i in range(same):
                # 中文词组长度
                chLen = struct.unpack('H', data[pos:pos+2])[0]
                pos += 2
                # 中文词组
                ch = self.byte2str(data[pos:pos+chLen])
                pos += chLen
                # 扩展数据长度
                extLen = struct.unpack('H', data[pos:pos+2])[0]
                pos += 2
                # 词频
                count = struct.unpack('H', data[pos:pos+2])[0]
                # 到下个词的偏移位置
                pos += extLen
                CallUtils.call(callback, count, py, ch)


    def pyWord(self, data, pyTab):
        pos, length, string = 0, len(data), ''
        while pos < length:
            index = struct.unpack('H', data[pos:pos+2])[0]
            string += pyTab[index]
            pos += 2
        return string


    def pyTable(self, data):
        if data[0x00:0x04] != bytes(map(ord, '\x9D\x01\x00\x00')):
            return None
        data = data[0x04:]
        pos, length, pyTab = 0, len(data), {}
        while pos < length:
            index = struct.unpack('H', data[pos:pos+2])[0]
            pos += 2
            l = struct.unpack('H', data[pos:pos+2])[0]
            pos += 2
            pyTab[index] = self.byte2str(data[pos:pos+l])
            pos += l
        return pyTab


    def byte2str(self, data):
        index, length, string = 0, len(data), ''
        while index < length:
            char =  chr(struct.unpack('H', data[index:index+2])[0])
            if char == '\r':
                string += '\n'
            elif char != ' ':
                string += char
            index += 2
        return string
