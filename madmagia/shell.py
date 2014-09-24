import os
import subprocess


class Process(object):
    def __init__(self, *args):
        self.args = args
        self.stdout = None
        self.stderr = None
        self.returncode = None

    def execute(self):
        p = subprocess.Popen(self.args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
        self.returncode = p.returncode


def execute(*args):
    p = Process(*args)
    p.execute()
    return p


def rm(f):
    if os.path.exists(f):
        os.remove(f)
