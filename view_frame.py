import os
import sys
import uuid
import tempfile
import subprocess

import sequence
import video_slice

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Args:'
        print >> sys.stderr, '    SOURCE_FILE TIME'
        sys.exit(1)
    imgf = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + '.png')
    if video_slice.save_frame(
            sys.argv[1], sequence.parse_time(sys.argv[2]), imgf):
        raise ValueError('Fail to extract frame')
    subprocess.Popen(['display', imgf])
