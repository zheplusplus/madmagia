import sys

import config
import export


def _sec_name():
    return sys.argv[1] if len(sys.argv) == 2 else None


def srt():
    export.srt(config.init_config(), sys.stdout, _sec_name())


def lrc():
    export.lrc(config.init_config(), sys.stdout, _sec_name())
