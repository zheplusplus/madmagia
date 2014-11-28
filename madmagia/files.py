import os
import re

_PREFIX_FLOAT = re.compile(r'(^[0-9]+\.[0-9]+)')
_PREFIX_INT = re.compile(r'(^[0-9]+)')


def epnum(fn):
    mat = _PREFIX_FLOAT.match(fn)
    if mat is not None:
        return float(mat.groups()[0])
    mat = _PREFIX_INT.match(fn)
    if mat is not None:
        return int(mat.groups()[0])
    raise ValueError('Unable to find index pattern of filename: ' + fn)


def _is_video(f, postfix):
    for p in postfix:
        if f.endswith(p):
            return True
    return False


def input_videos(video_dir, postfix_list):
    postfix_list = filter(None, postfix_list)
    return {epnum(f): os.path.join(video_dir, f)
            for f in os.listdir(video_dir) if _is_video(f, postfix_list)}
