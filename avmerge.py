import os
import uuid
import subprocess

import audio_slice
import video_slice
import sequence


def _merge_sections(sections, source_video_dir, audio_file, output_file):
    source_files = [os.path.join(source_video_dir, f)
                    for f in sorted(os.listdir(source_video_dir))]
    tmp_name_id = str(uuid.uuid4())
    video_file = video_slice.from_segments(
        source_files, tmp_name_id, sum([sec.segments for sec in sections], []))

    p = subprocess.Popen([
        'mencoder',
        '-audiofile', audio_file,
        '-of', 'lavf', '-lavfopts', 'format=mp4',
        '-oac', 'copy', '-ovc', 'x264',
        '-o', output_file,
        video_file])
    p.wait()
    if p.returncode != 0:
        raise ValueError('fail')
    return tmp_name_id


def merge_entire(sequence_file, source_video_dir, audio_file, output_file):
    with open(sequence_file, 'r') as f:
        sections, total_dur = sequence.parse(f.readlines())
    return _merge_sections(sections, source_video_dir, audio_file, output_file)


def _find_sec(sections, sec_name):
    for i, sec in enumerate(sections):
        if sec.name == sec_name:
            return i, sec
    raise ValueError('No such section: ' + sec_name)


def _interval_secs(sections, end_sec_name, begin_index, audio_file):
    if end_sec_name is None:
        try:
            next_sec = sections[begin_index + 1]
            return next_sec.start_time, sections[begin_index: begin_index + 1]
        except IndexError:
            return audio_slice.audio_len(audio_file), sections[begin_index:]
    if end_sec_name == ':end':
        return audio_slice.audio_len(audio_file), sections[begin_index:]
    end_index, end_section = _find_sec(sections, end_sec_name)
    if end_index < begin_index:
        raise ValueError('section disorder')
    return end_section.start_time, sections[begin_index: end_index]


def merge_partial(sequence_file, source_video_dir, audio_file, output_file,
                  begin_sec_name, end_sec_name=None):
    with open(sequence_file, 'r') as f:
        sections, total_dur = sequence.parse(f.readlines())
    begin_index, begin_section = _find_sec(sections, begin_sec_name)
    begin_time = begin_section.start_time
    end_time, sec_range = _interval_secs(sections, end_sec_name, begin_index,
                                         audio_file)
    sliced_audio = audio_slice.slice(audio_file, os.path.dirname(output_file),
                                     begin_time, end_time)
    _merge_sections(sec_range, source_video_dir, sliced_audio, output_file)
