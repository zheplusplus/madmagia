import os
import re
from pydub import AudioSegment

import pathutil
import sequence

_DURATION_RE = re.compile('Duration: (?P<h>[0-9]+):(?P<m>[0-9]+):' +
                          r'(?P<s>[0-9]+\.[0-9]+)')
OUTPUT_DIR = pathutil.fullpath(os.path.join('output', 'audio'))


def audio_len(f):
    return len(AudioSegment.from_mp3(f)) / 10 / 100.0


def _audio_from_to(input_file, name, ext, start, end, output_dir):
    output_path = os.path.join(output_dir, ''.join([
        'audio_', name, '_', str(start), '-', str(end), ext]))
    if pathutil.isfile(output_path):
        return output_path
    AudioSegment.from_mp3(input_file)[
        int(start * 1000): int(end * 1000)].export(output_path, format='mp3')
    return output_path


def slice(input_file, start, end_time, output_dir=OUTPUT_DIR):
    pathname, ext = os.path.splitext(input_file)
    return _audio_from_to(input_file, os.path.basename(pathname), ext,
                          start, end_time, output_dir)


def split(input_file, sequence_file):
    duration = audio_len(input_file)
    with open(sequence_file, 'r') as f:
        sections = sequence.parse(f.readlines(), False)[0]
    pathname, ext = os.path.splitext(input_file)
    name = os.path.basename(pathname)
    last_sec = sections[0]
    for sec in sections[1:]:
        if sec.start == last_sec.start:
            continue
        if sec.start < last_sec.start:
            raise ValueError('Section start time error: %s < %s' %
                             (sec.name, last_sec.name))
        if duration < sec.start:
            raise ValueError('Exceed audio duration ' + (sec.start))
        _audio_from_to(input_file, name, ext, last_sec.start, sec.start,
                       OUTPUT_DIR)
        last_sec = sec
    if duration == last_sec.start:
        return
    _audio_from_to(input_file, name, ext, last_sec.start, duration,
                   OUTPUT_DIR)
