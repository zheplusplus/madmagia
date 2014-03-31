import sys
import os
import re
import traceback

import avmerge
import sequence

_SECTION_PARSE = re.compile('(?P<begin>[^-]+)(-(?P<end>[^-]+)?)?')

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print >> sys.stderr, 'Args:'
        print >> sys.stderr, '    SEQUENCE_FILE INPUT_DIRECTORY INPUT_BGM',
        print >> sys.stderr, 'OUTPUT_PATH BEGIN_SECTION[-[END_SECTION]]'
        sys.exit(1)
    if os.path.exists(sys.argv[4]):
        print >> sys.stderr, sys.argv[4], 'already exists.'
        print >> sys.stderr, 'Please delete it to proceed.'
        sys.exit(1)
    section_args_match = _SECTION_PARSE.match(sys.argv[-1])
    if section_args_match is None:
        raise ValueError('Invalid sections')
    section_args = section_args_match.groupdict()
    try:
        avmerge.merge_partial(
            *(sys.argv[1:-1] + [section_args['begin'], section_args['end']]))
    except sequence.ParseError, e:
        traceback.print_exc()
        print >> sys.stderr, e.linenum, ':', e.message, ':', e.content
