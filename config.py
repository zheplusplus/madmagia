import ConfigParser

import pathutil


def _get_config(c, sec, opt, default=''):
    try:
        return c.get(sec, opt) or default
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default


def _init_config():
    conf_file = 'local.ini' if pathutil.isfile('local.ini') else 'config.ini'
    with open(conf_file, 'r') as conf_file:
        c = ConfigParser.ConfigParser()
        c.readfp(conf_file)
        return {
            'avconv': _get_config(c, 'exec', 'avconv'),
            'mencoder': _get_config(c, 'exec', 'mencoder'),
            'display': _get_config(c, 'exec', 'display'),
            'resolution': _get_config(c, 'video', 'resolution', '640:360'),
        }

config = _init_config()
