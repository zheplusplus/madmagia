import os
import sys
import logging
import ConfigParser
import tempfile
from datetime import datetime

import pathutil
import sequence
import files


def _get_config(c, sec, opt, default=''):
    try:
        return c.get(sec, opt) or default
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default


def _logger(c):
    try:
        level = getattr(logging, _get_config(
            c, 'logging', 'level', 'info').upper())
    except (AttributeError, ValueError):
        raise ValueError('Invalid logging level: %s' % level_rep)
    logger = logging.getLogger('madmagia')
    logger.setLevel(level)

    logfile = _get_config(c, 'logging', 'file', None)
    if not logfile:
        logfile = os.path.join(tempfile.gettempdir(),
                               datetime.now().strftime('mmtmp_%Y-%m-%d.log'))
    handler = logging.FileHandler(logfile)
    logger.addHandler(handler)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logging.debug('Logging to %s', logfile)
    return logger


def _init_config():
    with open('config.ini', 'r') as conf_file:
        c = ConfigParser.ConfigParser()
        c.readfp(conf_file)
        if not _get_config(c, 'input', 'video_dir'):
            raise ValueError('video_dir not specified')
        video_dir = pathutil.fullpath(_get_config(c, 'input', 'video_dir'))
        return {
            'video_dir': video_dir,
            'input_videos': files.input_videos(
                video_dir, _get_config(c, 'input', 'video_postfix',
                                       'mov,mkv,mp4,avi,rm,rmvb').split(',')),
            'bgm': pathutil.fullpath(_get_config(c, 'input', 'bgm')),
            'sequence': pathutil.fullpath(_get_config(c, 'input', 'sequence')),
            'avconv': _get_config(c, 'exec', 'avconv'),
            'mencoder': _get_config(c, 'exec', 'mencoder'),
            'display': _get_config(c, 'exec', 'display'),
            'resolution': _get_config(c, 'output', 'resolution', '640:360'),
            'bitrate': _get_config(c, 'output', 'bitrate', '1.6M'),
            'fps': _get_config(c, 'output', 'fps', '24'),
            'vcodec': _get_config(c, 'output', 'vcodec', 'copy'),
        }, _logger(c)

config, logger = _init_config()
logger.debug('Videos ep map:')
for ep, f in config['input_videos'].iteritems():
    logger.debug('  %s: %s' % (ep, f))
