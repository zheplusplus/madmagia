import os


def fullpath(p):
    return os.path.realpath(os.path.expanduser(p))


def isdir(p):
    return os.path.isdir(os.path.expanduser(p))


def isfile(p):
    return os.path.isfile(os.path.expanduser(p))
