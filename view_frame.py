import os
import sys
import subprocess

import sequence
import video_slice
from config import config

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Args:'
        print >> sys.stderr, '    SOURCE_FILE TIME'
        sys.exit(1)
    imgf = video_slice.save_frame(
        sys.argv[1], sequence.parse_time(sys.argv[2]))
    if imgf is None:
        raise ValueError('Fail to extract frame')
    subprocess.Popen([config['display'], imgf])
