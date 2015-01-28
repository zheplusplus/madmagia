import os.path
import logging

import pathutil
import shell

_vfilters = dict()
VIDEO_OUTPUT_DIR = pathutil.fullpath(os.path.join('output', 'video'))
FRAME_OUTPUT_DIR = pathutil.fullpath(os.path.join('output', 'frame'))


def _vfilter(f):
    _vfilters[f.__name__[1:].lower()] = f
    return f


@_vfilter
def _repeatframe(config, i, seg, inp, args):
    image = save_frame_to(config, 0, inp, inp + '_rf.png')
    tmp_file = inp + '_repeat_frame.mp4'
    if os.path.exists(tmp_file):
        return tmp_file
    p = shell.execute(
        config['avconv'],
        '-loop', '1',
        '-i', image,
        '-vcodec', config['vcodec'],
        '-t', str(seg.duration),
        '-vf', 'scale=' + config['resolution'],
        '-b:v', config['bitrate'],
        '-r', config['fps'],
        tmp_file)
    if p.returncode != 0:
        raise ValueError('process fail at %d : %s' % (i, p.stderr))
    return tmp_file


@_vfilter
def _hflip(config, i, seg, inp, args):
    tmp_file = inp + '_hflip.mp4'
    if os.path.exists(tmp_file):
        return tmp_file
    p = shell.execute(
        config['avconv'],
        '-i', inp,
        '-vcodec', config['vcodec'],
        '-vf', 'hflip',
        '-b:v', config['bitrate'],
        '-r', config['fps'],
        tmp_file)
    if p.returncode != 0:
        raise ValueError('process fail at %d : %s' % (i, p.stderr))
    return tmp_file


@_vfilter
def _fillspan(config, i, seg, inp, span_dur):
    pts_rate = span_dur / float(seg.duration)
    tmp_file = inp + '_fillspan' + str(span_dur) + '.mp4'
    if os.path.exists(tmp_file):
        return tmp_file
    p = shell.execute(
        config['avconv'],
        '-i', inp,
        '-vcodec', config['vcodec'],
        '-vf', 'setpts=PTS*' + str(pts_rate),
        '-b:v', config['bitrate'],
        '-r', config['fps'],
        tmp_file)
    if p.returncode != 0:
        raise ValueError('process fail at %d : %s' % (i, p.stderr))
    return tmp_file


def save_frame(config, time, epnum):
    return save_frame_to(
        config, time, config['input_videos'][epnum],
        os.path.join(FRAME_OUTPUT_DIR, '%s_%f.png' % (epnum, time)))


def save_frame_to(config, time, source_file, output_file):
    if os.path.exists(output_file):
        logging.debug('Cached image %s', output_file)
        return output_file
    args = [
        config['avconv'],
        '-ss', str(time),
        '-i', source_file,
        '-vsync', '1',
        '-t', '0.01',
    ]
    if config['resolution']:
        args.extend(['-s', config['resolution'].replace(':', 'x')])
    args.append(output_file)
    p = shell.execute(*args)
    if p.returncode != 0 and 'filename number 2 from pattern' not in p.stderr:
        raise shell.ShellError(args, p.stderr)
    logging.debug('Generated image %s', output_file)
    return output_file


def _cut_segment(config, i, seg, output_dir):
    tmp_file = os.path.join(output_dir, 'segment_%s_%f_%f.mp4' % (
        seg.epnum, seg.start, seg.duration))
    if os.path.exists(tmp_file):
        logging.info('Cached segment: %d - %s', i, tmp_file)
        return tmp_file

    if seg.epnum not in config['input_videos']:
        raise ValueError('Process fail at ' + str(i) + ': no such epnum ' +
                         seg.epnum)
    source_file = config['input_videos'][seg.epnum]
    args = [
        config['avconv'],
        '-ss', str(seg.start),
        '-i', source_file,
        '-t', str(seg.duration),
        '-vf', 'scale=' + config['resolution'],
        '-vcodec', config['vcodec'],
        '-b:v', config['bitrate'],
        '-r', config['fps'],
        '-an', tmp_file,
    ]
    p = shell.execute(*args)
    if p.returncode != 0:
        raise shell.ShellError(args, 'process fail at %d : %s' % (i, p.stderr))
    logging.info('Generated segment: %d - %s', i, tmp_file)
    return tmp_file


def slice_segment(config, i, seg, output_dir):
    return _apply_filters(
        config, _cut_segment(config, i, seg, output_dir), i, seg)


def _apply_filters(config, tmp_file, i, seg):
    for vfilter_args in seg.filters:
        vfilter = vfilter_args[0].lower()
        args = vfilter_args[1]
        if vfilter not in _vfilters:
            raise ValueError('No such filter: ' + vfilter)
        tmp_file = _vfilters[vfilter](config, i, seg, tmp_file, args)
    return tmp_file


def slice_segments(config, segments, output_dir=VIDEO_OUTPUT_DIR):
    tmp_files = []
    for i, seg in enumerate(segments):
        tmp_files.append(slice_segment(config, i, seg, output_dir))
        if (i + 1) % 20 == 0:
            logging.info('Produced segments %d / %d', i + 1, len(segments))
    return tmp_files


def merge_segments(config, files, output_dir=VIDEO_OUTPUT_DIR):
    merged_video = os.path.join(output_dir, 'merged.mp4')
    if len(files) == 0:
        raise ValueError('no segments')
    logging.info('Merging segments to %s', merged_video)
    pathutil.rm(merged_video)
    p = shell.execute(
        config['mencoder'],
        '-ovc', 'copy',
        '-o', merged_video,
        *files)
    if p.returncode != 0:
        raise ValueError('fail\n' + p.stderr)
    return merged_video
