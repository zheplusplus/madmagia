import logging
import ConfigParser

import pathutil
import files


def _get_config(c, sec, opt, default=''):
    try:
        return c.get(sec, opt) or default
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default


def init_logger(level_rep):
    try:
        level = getattr(logging, level_rep.upper())
    except (AttributeError, ValueError):
        raise ValueError('Invalid logging level: %s' % level_rep)
    logging.basicConfig(
        level=level, format='%(levelname)s:%(asctime)s:%(message)s')


def make_config(video_dir, video_postfixes, bgm, sequence_file,
                avconv, mencoder, display,
                resolution, bitrate, fps, vcodec):
    return {
        'video_dir': video_dir,
        'input_videos': files.input_videos(video_dir, video_postfixes),
        'bgm': bgm,
        'sequence': sequence_file,
        'avconv': avconv,
        'mencoder': mencoder,
        'display': display,
        'resolution': resolution,
        'bitrate': bitrate,
        'fps': str(fps),
        'vcodec': vcodec or 'copy',
    }


def init_config():
    with open('config.ini', 'r') as conf_file:
        c = ConfigParser.ConfigParser()
        c.readfp(conf_file)
        if not _get_config(c, 'input', 'video_dir'):
            raise ValueError('video_dir not specified')
        video_dir = pathutil.fullpath(_get_config(c, 'input', 'video_dir'))
        init_logger(_get_config(c, 'logging', 'level', 'info'))
        return make_config(
            pathutil.fullpath(_get_config(c, 'input', 'video_dir')),
            _get_config(c, 'input', 'video_postfix',
                        'mov,mkv,mp4,avi,rm,rmvb').split(','),
            pathutil.fullpath(_get_config(c, 'input', 'bgm')),
            pathutil.fullpath(_get_config(c, 'input', 'sequence')),

            _get_config(c, 'exec', 'avconv'),
            _get_config(c, 'exec', 'mencoder'),
            _get_config(c, 'exec', 'display'),

            _get_config(c, 'output', 'resolution', '640:360'),
            _get_config(c, 'output', 'bitrate', '1.6M'),
            _get_config(c, 'output', 'fps', 30),
            _get_config(c, 'output', 'vcodec', 'copy'),
        )
