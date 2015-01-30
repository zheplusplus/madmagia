import os
import shutil

import avmerge
import audio_slice
import sequence


def export_to(config, p):
    files = avmerge.slice_partial(
        config, avmerge.find_range(config, ':begin', ':end')[2])
    for i, f in enumerate(files):
        shutil.copy(f, os.path.join(p, 'mmexport_%03d.mp4' % i))


def _time_srt(t):
    seconds = int(t)
    millis = int(1000 * (t - seconds))
    return ''.join([str(seconds / 3600), ':', str(seconds % 3600 / 60), ':',
                    str(seconds % 60), ',', str(millis)])


def _echo_srt(out, i, section, _, end_time):
    if section.sub:
        print >> out, i
        print >> out, _time_srt(section.start), '-->', _time_srt(end_time)
        print >> out, section.sub.replace('\\n', '\n')
        print >> out, ''


def _time_lrc(t):
    seconds = int(t)
    millis = t - seconds
    return '[%02d:%05.2f]' % (seconds % 3600 / 60, seconds % 60 + millis)


def _echo_lrc(out, i, section, next_section, end_time):
    if section.sub:
        print >> out, _time_lrc(section.start), section.sub.replace('\\n', ' ')
        if next_section and not next_section.sub:
            print >> out, _time_lrc(next_section.start)


def _output(config, echo, out, sec_name):
    with open(config['sequence'], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines(), False)
    if len(sections) == 0:
        raise ValueError('no sections')

    time_off = 0
    i = 0
    if sec_name is not None:
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
        echo(out, i + 1, s, sections[i + 1], sections[i + 1].start)
    echo(out, len(sections), sections[-1], None,
         audio_slice.audio_len(config['bgm']))


def srt(config, out, sec_name):
    _output(config, _echo_srt, out, sec_name)


def lrc(config, out, sec_name):
    _output(config, _echo_lrc, out, sec_name)
