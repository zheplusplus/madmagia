import sys
import os.path

import pathutil

DEFAULT_CONFIG = '''[input]
video_dir=
video_postfix=mov,mkv,mp4,avi,rm,rmvb
bgm=
sequence=./sequence.txt
[exec]
avconv=avconv
mencoder=mencoder
display=display
[output]
resolution=1280:720
bitrate=1.6M
fps=30
vcodec=mpeg4
[logging]
level=info
'''

DEFAULT_SEQUENCE = '''# Sequence example file
# Lines started with # will be ignored

# Section example

#         TIME    NAME      SUBTITLES (optional)
#:section 01:00.0 section_a any text would be ok

# Segment example

# EPISODE TIME    DURATION
#      01 00:02.0 4.0
'''


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

    with open('config.ini', 'w') as f:
        f.write(DEFAULT_CONFIG)
    with open('sequence.txt', 'w') as f:
        f.write(DEFAULT_SEQUENCE)


def clean():
    pathutil.rm_all('output/video')
