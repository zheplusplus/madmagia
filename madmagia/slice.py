import sys
import re
import logging

import avmerge
import export
import sequence
import audio_slice
import pathutil
import config

_SECTION_PARSE = re.compile('(?P<begin>[^-]+)(-(?P<end>[^-]+)?)?')


def _sec_args():
    if len(sys.argv) == 1:
        begin_sec = ':begin'
        end_sec = ':end'
        return ':begin', ':end'
    if len(sys.argv) == 2:
        return sys.argv[1], sys.argv[1]
    return sys.argv[1], sys.argv[2]


def slice():
    begin_sec, end_sec = _sec_args()
    print 'Use sections', begin_sec, '->', end_sec
    try:
        avmerge.merge_partial(config.init_config(), begin_sec, end_sec)
    except sequence.ParseError, e:
        logging.exception(e)
        print >> sys.stderr, e.linenum, ':', e.message, ':', e.content


def inspect():
    conf = config.init_config()
    begin_sec, end_sec = _sec_args()
    print 'Use sections', begin_sec, '->', end_sec
    try:
        _, end_time, sections = avmerge.find_range(conf, begin_sec, end_sec)
        if len(sections) == 0:
            return
        sliced_segs = avmerge.slice_partial(conf, sections)
    except sequence.ParseError, e:
        logging.exception(e)
        print >> sys.stderr, e.linenum, ':', e.message, ':', e.content
        return

    def next_section(sec_index, seg_index, expected_len, actual_len):
        sec = sections[sec_index]
        print ':.:', sec.name
        sec_len = 0.0
        for seg in sec.segments:
            seg_len = audio_slice.audio_len(sliced_segs[seg_index])
            print '  >', seg.duration, seg_len
            sec_len += seg_len
            seg_index += 1
        actual_len += sec_len
        if sec_index == len(sections) - 1:
            expected_len += end_time - sec.start
            print '  :', end_time - sec.start, sec_len,
            print ':', expected_len, actual_len, actual_len - expected_len
            return
        expected_len += sections[sec_index + 1].start - sec.start
        print '  :', sections[sec_index + 1].start - sec.start, sec_len,
        print ':', expected_len, actual_len, actual_len - expected_len
        next_section(sec_index + 1, seg_index, expected_len, actual_len)

    next_section(0, 0, 0, 0)


def export_segs():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Args:'
        print >> sys.stderr, '    OUTPUT_DIRECTORY'
        return sys.exit(1)
    if not pathutil.isdir(sys.argv[1]):
        print >> sys.stderr, sys.argv[1], 'is not a directory'
        return sys.exit(1)
    try:
        export.export_to(config.init_config(), sys.argv[1])
    except sequence.ParseError, e:
        logging.exception(e)
        print >> sys.stderr, e.linenum, ':', e.message, ':', e.content
