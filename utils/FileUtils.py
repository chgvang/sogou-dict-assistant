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
        parent = os.path.dirname(path)
        return FileUtils.relpath(parent, name)

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
    def count_lines(path):
        count = 0
        with FileUtils.open_reader(path) as reader:
            for _ in reader:
                count += 1
        return count

    @staticmethod
    def open_writer(path, mode='w'):
        return open(path, mode)

    @staticmethod
    def close_writer(*writers):
        [writer.flush() for writer in writers]
        FileUtils.close(*writers)

    @staticmethod
    def open_reader(path, mode='r'):
        return open(path, mode)

    @staticmethod
    def close(*files):
        [file.close() for file in files]
