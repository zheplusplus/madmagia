import sys
import shutil
import os.path

import pathutil

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'asset', 'config.ini')
SEQ_FILE = os.path.join(os.path.dirname(__file__), 'asset', 'sequence.txt')


def main():
    if os.path.exists('config.ini'):
        print >> sys.stderr, './config.ini already exists'
        return sys.exit(1)
    if os.path.exists('sequence.txt'):
        print >> sys.stderr, './sequence.txt already exists'
        return sys.exit(1)
    if os.path.exists('output'):
        print >> sys.stderr, './output already exists'
        return sys.exit(1)

    try:
        os.makedirs('output/audio')
        os.makedirs('output/video')
        os.makedirs('output/frame')
    except OSError, e:
        print >> sys.stderr, 'fail to make one of the output subdirectories'
        print >> sys.stderr, e
        print >> sys.stderr, 'please remove ./output/ directory and try again'
        return sys.exit(1)

    shutil.copyfile(CONFIG_FILE, 'config.ini')
    shutil.copyfile(SEQ_FILE, 'sequence.txt')


def clean():
    pathutil.rm_all('output/audio')
    pathutil.rm_all('output/video')
    pathutil.rm_all('output/frame')
