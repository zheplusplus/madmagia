import sys

import pathutil
import audio_slice

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >> sys.stderr, 'Args: INPUT_AUDIO_FILE SEQUENCE_FILE OUTPUT_DIR'
        sys.exit(1)
    if not pathutil.isdir(sys.argv[3]):
        print >> sys.stderr, sys.argv[3], 'is not a directory'
        sys.exit(1)
    audio_slice.split(pathutil.fullpath(sys.argv[1]),
                      pathutil.fullpath(sys.argv[2]),
                      pathutil.fullpath(sys.argv[3]))
