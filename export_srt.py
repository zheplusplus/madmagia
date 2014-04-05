import os
import sys
import subprocess

import sequence
import video_slice


def format_time(t):
    seconds = int(t)
    millis = int(1000 * (t - seconds))
    return ''.join([str(seconds / 3600), ':', str(seconds % 3600 / 60), ':',
                    str(seconds % 60), ',', str(millis)])


def write_section(i, section, next_sec):
    print i
    print format_time(section.start_time), '-->',
    print format_time(next_sec.start_time)
    print section.sub
    print ''


def convert_srt(sections):
    for i, s in enumerate(sections[:-1]):
        write_section(i, s, sections[i + 1])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Args:'
        print >> sys.stderr, '    SEQUENCE_FILE'
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines())
    convert_srt(sections)
