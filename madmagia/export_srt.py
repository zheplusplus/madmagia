import os
import sys

from config import config
import sequence
import video_slice
import audio_slice


def _time_srt(t):
    seconds = int(t)
    millis = int(1000 * (t - seconds))
    return ''.join([str(seconds / 3600), ':', str(seconds % 3600 / 60), ':',
                    str(seconds % 60), ',', str(millis)])


def _echo_srt(i, section, _, end_time):
    if section.sub:
        print i
        print _time_srt(section.start), '-->', _time_srt(end_time)
        print section.sub.replace('\\n', '\n')
        print ''


def _output(echo):
    with open(config['sequence'], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines())
    if len(sections) == 0:
        raise ValueError('no sections')

    time_off = 0
    i = 0
    if len(sys.argv) == 2:
        sec_name = sys.argv[1]
        for i, s in enumerate(sections):
            if sec_name == s.name:
                time_off = s.start
                break
        else:
            raise ValueError('no such section %s' % sec_name)

        sections = sections[i:]
        for s in sections:
            s.start -= time_off

    for i, s in enumerate(sections[:-1]):
        echo(i + 1, s, sections[i + 1], sections[i + 1].start)
    echo(len(sections), sections[-1], None,
         audio_slice.audio_len(config['bgm']))


def srt():
    _output(_echo_srt)


def _time_lrc(t):
    seconds = int(t)
    millis = t - seconds
    return '[%02d:%05.2f]' % (seconds % 3600 / 60, seconds % 60 + millis)


def _echo_lrc(i, section, next_section, end_time):
    if section.sub:
        print _time_lrc(section.start), section.sub.replace('\\n', ' ')
        if next_section and not next_section.sub:
            print _time_lrc(next_section.start)


def lrc():
    _output(_echo_lrc)
