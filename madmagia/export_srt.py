import os
import sys

from config import config
import sequence
import video_slice
import audio_slice


def format_time(t):
    seconds = int(t)
    millis = int(1000 * (t - seconds))
    return ''.join([str(seconds / 3600), ':', str(seconds % 3600 / 60), ':',
                    str(seconds % 60), ',', str(millis)])


def echo_section(i, section, end_time):
    if section.sub:
        print i
        print format_time(section.start), '-->', format_time(end_time)
        print section.sub.replace('\\n', '\n')
        print ''


def main():
    with open(config['sequence'], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines())
    if len(sections) == 0:
        raise ValueError('no sections')
    for i, s in enumerate(sections[:-1]):
        echo_section(i + 1, s, sections[i + 1].start)
    echo_section(len(sections), sections[-1],
                 audio_slice.audio_len(config['bgm']))
