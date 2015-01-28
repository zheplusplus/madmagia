import logging

import audio_slice
import video_slice
import sequence
import pathutil
import shell

OUTPUT_FILE = pathutil.fullpath('./output/output.mp4')


def avmerge(config, audio_file, video_file, output_file=OUTPUT_FILE,
            force_encoder=None, sync=True):
    logging.info('Zip video and audio')
    pathutil.rm(output_file)
    args = [
        config['avconv'],
        '-i', audio_file,
        '-i', video_file,
        '-acodec', 'copy',
        '-vcodec', 'copy' if force_encoder is None else force_encoder,
        output_file]
    p = shell.Process(args, sync)
    p.execute()
    if sync and p.returncode != 0:
        raise shell.ShellError(args, p.stderr)
    return output_file


def _merge_sections(config, sections, audio_file):
    video_file = video_slice.merge_segments(
        config, slice_partial(config, sections))
    return avmerge(config, audio_file, video_file)


def _find_sec(config, sections, sec_name):
    for i, sec in enumerate(sections):
        if sec.name == sec_name:
            return i, sec
    raise ValueError('No such section: ' + sec_name)


def _interval_secs(config, sections, end_sec_name, begin_index):
    if end_sec_name == ':end':
        return audio_slice.audio_len(config['bgm']), sections[begin_index:]
    end_index, end_section = _find_sec(config, sections, end_sec_name)
    if end_index + 1 == len(sections):
        return audio_slice.audio_len(config['bgm']), sections[begin_index:]
    if end_index < begin_index:
        raise ValueError('section disorder')
    return sections[end_index + 1].start, sections[begin_index: end_index + 1]


def slice_partial(config, sections):
    return video_slice.slice_segments(
        config, sum([sec.segments for sec in sections], []))


def find_range(config, begin_sec_name, end_sec_name):
    with open(config['sequence'], 'r') as f:
        sections, total_dur = sequence.parse(f.readlines(), True)
    begin_index, begin_section = _find_sec(config, sections, begin_sec_name)
    begin_time = begin_section.start
    end_time, sec_range = _interval_secs(
        config, sections, end_sec_name, begin_index)
    return begin_time, end_time, sec_range


def merge_partial(config, begin_sec_name, end_sec_name):
    begin_time, end_time, sec_range = find_range(
        config, begin_sec_name, end_sec_name)
    _merge_sections(config, sec_range,
                    audio_slice.slice(config['bgm'], begin_time, end_time))
