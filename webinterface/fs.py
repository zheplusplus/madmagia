import os
import sys
import json
import shutil

import app

try:
    import _winreg


    def _fs_roots():
        res = []
        deviceID = ''
        subKey = 'SYSTEM\MountedDevices'

        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, subKey)
        i = 0
        try:
            while True:
                name, value, type = _winreg.EnumValue(key, i)
                if name.startswith('\\DosDevices\\'):
                    res.append((name, repr(value)[1: 17]))
                    if name.startswith('\\DosDevices\\C'):
                        deviceID = repr(value)[1: 17]
                i += 1
        except WindowsError:
            pass
        res = filter(lambda item : item[1] == deviceID, res)
        res = zip(*res)[0]
        index = res[0].rindex('\\')
        res = sorted([item[index + 1: -1] for item in res])
        return [r + ':' for r in res]
except ImportError:
    class WindowsError(OSError):
        pass


    def _fs_roots():
        return ['/']


def _ls(path, dir_only):
    if len(path) == 2 and ('A' <= path[0] <= 'Z') and path[1] == ':':
        path += '\\'
    if os.path.isfile(path):
        path = os.path.dirname(path)
    def file_obj(o):
        absp = os.path.abspath(os.path.join(path, o))
        f = os.path.isfile(absp)
        if dir_only and f:
            return None
        return {'type': 'f' if f else 'd', 'path': absp}
    return filter(None, [file_obj(o) for o in os.listdir(path)])


def _mkdir(path):
    try:
        os.mkdir(path)
    except (OSError, WindowsError), e:
        raise ValueError(e.message)


@app.get_async('/ls/')
def ls(r):
    path = r.args['path']
    if not path:
        return [{'path': o, 'type': 'd'} for o in _fs_roots()]
    return _ls(path, r.args.get('dirOnly') == '1')


@app.post_async('/mkdir')
def mkdir(r):
    return _mkdir(r.form['path'])


@app.post_async('/clearcached')
def clear_cached(r):
    shutil.rmtree(app.temp_dir)
    app.sure_mkdir(app.temp_dir)
