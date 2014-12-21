import os

from config import config, logger
import audio_slice
import video_slice
import sequence
import pathutil
import shell

OUTPUT_FILE = pathutil.fullpath('./output/output.mp4')


def avmerge(audio_file, video_file, output_file=OUTPUT_FILE,
            force_encoder=None, sync=True):
    logger.info('Zip video and audio')
    pathutil.rm(output_file)
    p = shell.Process([
        config['avconv'],
        '-i', audio_file,
        '-i', video_file,
        '-acodec', 'copy',
        '-vcodec', 'copy' if force_encoder is None else force_encoder,
        output_file], sync)
    p.execute()
    if sync and p.returncode != 0:
        raise ValueError('fail')
    return output_file


def _merge_sections(sections, audio_file):
    video_file = video_slice.merge_segments(slice_partial(sections))
    return avmerge(audio_file, video_file)


def _find_sec(sections, sec_name):
    for i, sec in enumerate(sections):
        if sec.name == sec_name:
            return i, sec
    raise ValueError('No such section: ' + sec_name)


def _interval_secs(sections, end_sec_name, begin_index):
    if end_sec_name == ':end':
        return audio_slice.audio_len(config['bgm']), sections[begin_index:]
    end_index, end_section = _find_sec(sections, end_sec_name)
    if end_index + 1 == len(sections):
        return audio_slice.audio_len(config['bgm']), sections[begin_index:]
    if end_index < begin_index:
        raise ValueError('section disorder')
    return sections[end_index + 1].start, sections[begin_index: end_index + 1]


def slice_partial(sections):
    return video_slice.slice_segments(
        config['input_videos'], sum([sec.segments for sec in sections], []))


def find_range(begin_sec_name, end_sec_name):
    with open(config['sequence'], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines(), True)
    begin_index, begin_section = _find_sec(sections, begin_sec_name)
    begin_time = begin_section.start
    end_time, sec_range = _interval_secs(sections, end_sec_name, begin_index)
    return begin_time, end_time, sec_range


def merge_partial(begin_sec_name, end_sec_name):
    begin_time, end_time, sec_range = find_range(begin_sec_name, end_sec_name)
    _merge_sections(sec_range, audio_slice.slice(
        config['bgm'], begin_time, end_time))
