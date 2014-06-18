import os
import re

from config import config
import pathutil
import sequence
import shell

_DURATION_RE = re.compile('Duration: (?P<h>[0-9]+):(?P<m>[0-9]+):' +
                          r'(?P<s>[0-9]+\.[0-9]+)')
OUTPUT_DIR = pathutil.fullpath(os.path.join('output', 'audio'))


def audio_len(f):
    p = shell.execute(config['avconv'], '-i', f)
    dur_match = _DURATION_RE.search(p.stderr)
    if dur_match is None:
        raise ValueError('Unsupported audio file ' + f)
    dur_groups = dur_match.groupdict()
    return (int(dur_groups['h']) * 60 * 60 + int(dur_groups['m']) * 60 +
            float(dur_groups['s']))


def _audio_from_to(input_file, name, ext, start, end):
    output_path = os.path.join(OUTPUT_DIR, ''.join([
        name, '_', str(start), '-', str(end), ext]))
    if pathutil.isfile(output_path):
        return output_path
    p = shell.execute(
        config['avconv'],
        '-ss', str(start),
        '-i', input_file,
        '-t', str(end - start),
        output_path)
    if p.returncode != 0:
        raise ValueError('Process fail at section')
    return output_path


def slice(input_file, start, end_time):
    pathname, ext = os.path.splitext(input_file)
    name = os.path.basename(pathname)
    return _audio_from_to(input_file, name, ext, start, end_time)


def split(input_file, sequence_file):
    duration = audio_len(input_file)
    with open(sequence_file, 'r') as f:
        sections = sequence.parse(f.readlines())[0]
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
        _audio_from_to(input_file, name, ext, last_sec.start, sec.start)
        last_sec = sec
    if duration == last_sec.start:
        return
    _audio_from_to(input_file, name, ext, last_sec.start, duration)
