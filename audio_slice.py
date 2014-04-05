import os
import subprocess
import re

from config import config
import pathutil
import sequence

_DURATION_RE = re.compile('Duration: (?P<h>[0-9]+):(?P<m>[0-9]+):' +
                          r'(?P<s>[0-9]+\.[0-9]+)')


def audio_len(f):
    p = subprocess.Popen([config['avconv'], '-i', f], stderr=subprocess.PIPE)
    dur_match = _DURATION_RE.search(p.stderr.read())
    if dur_match is None:
        raise ValueError('Unsupported audio file')
    dur_groups = dur_match.groupdict()
    return (int(dur_groups['h']) * 60 * 60 + int(dur_groups['m']) * 60 +
            float(dur_groups['s']))


def _audio_from_to(input_file, output_dir, name, ext, start_time, end_time):
    output_path = os.path.join(output_dir, ''.join([
        name, '_', str(start_time), '-', str(end_time), ext]))
    if pathutil.isfile(output_path):
        return output_path
    p = subprocess.Popen([
        config['avconv'],
        '-ss', str(start_time),
        '-i', input_file,
        '-t', str(end_time - start_time),
        output_path])
    p.wait()
    if p.returncode != 0:
        raise ValueError('Process fail at section')
    return output_path


def slice(input_file, output_dir, start_time, end_time):
    pathname, ext = os.path.splitext(input_file)
    name = os.path.basename(pathname)
    return _audio_from_to(input_file, output_dir, name, ext, start_time,
                          end_time)


def split(input_file, sequence_file, output_dir):
    duration = audio_len(input_file)
    with open(sequence_file, 'r') as f:
        sections = sequence.parse(f.readlines())[0]
    pathname, ext = os.path.splitext(input_file)
    name = os.path.basename(pathname)
    last_sec = sections[0]
    for sec in sections[1:]:
        if sec.start_time == last_sec.start_time:
            continue
        if sec.start_time < last_sec.start_time:
            raise ValueError('Section start time error: %s < %s' %
                             (sec.name, last_sec.name))
        if duration < sec.start_time:
            raise ValueError('Exceed audio duration ' + (sec.start_time))
        _audio_from_to(input_file, output_dir, name, ext, last_sec.start_time,
                       sec.start_time)
        last_sec = sec
    if duration == last_sec.start_time:
        return
    _audio_from_to(input_file, output_dir, name, ext, last_sec.start_time,
                   duration)
