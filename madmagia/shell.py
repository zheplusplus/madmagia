import os
import sys
import subprocess

from pathutil import PATH_ENCODING


class Process(object):
    def __init__(self, *args):
        self.args = [a.encode(PATH_ENCODING) if isinstance(a, unicode) else a
                     for a in args]
        self.stdout = None
        self.stderr = None
        self.returncode = None

    def execute(self):
        try:
            p = subprocess.Popen(self.args, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            self.stdout, self.stderr = p.communicate()
            self.returncode = p.returncode
        except OSError:
            print >> sys.stderr, 'Error on executing:'
            print >> sys.stderr, ' '.join(self.args)
            raise


def execute(*args):
    p = Process(*args)
    p.execute()
    return p
