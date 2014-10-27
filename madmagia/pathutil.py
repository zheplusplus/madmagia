import os


def fullpath(p):
    return os.path.realpath(os.path.expanduser(p))


def isdir(p):
    return os.path.isdir(os.path.expanduser(p))


def isfile(p):
    return os.path.isfile(os.path.expanduser(p))


def rm(f):
    if os.path.exists(f):
        os.remove(f)


def rm_all(d):
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
