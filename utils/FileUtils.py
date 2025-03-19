#!/usr/bin/env python3
import os


class FileUtils(object):
    @staticmethod
    def exists(path):
        return os.path.exists(path)


    @staticmethod
    def isdir(path):
        return os.path.isdir(path)


    @staticmethod
    def isfile(path):
        return os.path.isfile(path)


    @staticmethod
    def mkdir(path):
        if FileUtils.exists(path) and not FileUtils.isdir(path):
            os.remove(path)
        if not FileUtils.exists(path):
            os.makedirs(path)


    @staticmethod
    def rename(path, name):
        href = FileUtils.href(path, name)
        os.renames(path, href)


    @staticmethod
    def href(path, name):
        dir = os.path.dirname(path)
        return FileUtils.relpath(dir, name)


    @staticmethod
    def relpath(path, *names):
        return os.path.join(path, *names)


    @staticmethod
    def subdirs(path):
        dirs, subs = [], sorted(os.listdir(path))
        for sub in subs:
            if FileUtils.isdir(FileUtils.relpath(path, sub)):
                dirs.append(sub)
        return dirs


    @staticmethod
    def subfiles(path):
        files, subs = [], sorted(os.listdir(path))
        for sub in subs:
            if FileUtils.isfile(FileUtils.relpath(path, sub)):
                files.append(sub)
        return files


    @staticmethod
    def countLines(path):
        count = 0
        with FileUtils.openReader(path) as reader:
            for line in reader:
                count += 1
        return count


    @staticmethod
    def openWriter(path, mode = 'w'):
        return open(path, mode)


    @staticmethod
    def closeWriter(*writers):
        [writer.flush() for writer in writers]
        FileUtils.close(*writers)


    @staticmethod
    def openReader(path, mode = 'r'):
        return open(path, mode)


    @staticmethod
    def close(*files):
        [file.close() for file in files]
