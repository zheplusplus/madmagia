import os
import sys
import logging
import ConfigParser

import pathutil
import sequence


def _get_config(c, sec, opt, default=''):
    try:
        return c.get(sec, opt) or default
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default


def _input_videos(video_dir):
    return {sequence.epnum(f): os.path.join(video_dir, f)
            for f in os.listdir(video_dir)}


def _logger():
    logger = logging.getLogger('madmagia')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def _init_config():
    conf_file = 'local.ini' if pathutil.isfile('local.ini') else 'config.ini'
    with open(conf_file, 'r') as conf_file:
        c = ConfigParser.ConfigParser()
        c.readfp(conf_file)
        if not _get_config(c, 'input', 'video_dir'):
            raise ValueError('video_dir not specified')
        video_dir = pathutil.fullpath(_get_config(c, 'input', 'video_dir'))
        return {
            'video_dir': video_dir,
            'input_videos': _input_videos(video_dir),
            'bgm': pathutil.fullpath(_get_config(c, 'input', 'bgm')),
            'sequence': pathutil.fullpath(_get_config(c, 'input', 'sequence')),
            'avconv': _get_config(c, 'exec', 'avconv'),
            'mencoder': _get_config(c, 'exec', 'mencoder'),
            'display': _get_config(c, 'exec', 'display'),
            'resolution': _get_config(c, 'output', 'resolution', '640:360'),
            'bitrate': _get_config(c, 'output', 'bitrate', '1.6M'),
            'fps': _get_config(c, 'output', 'fps', '24'),
            'vcodec': _get_config(c, 'output', 'vcodec', 'copy'),
        }, _logger()

config, logger = _init_config()
