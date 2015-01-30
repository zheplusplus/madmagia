import os
import shutil
import string

import app

if os.name == 'nt':
    def _fs_roots():
        roots = []
        for i in xrange(24):
            try:
                os.listdir(string.uppercase[i + 2] + ':')
                roots.append(string.uppercase[i + 2] + ':')
            except WindowsError:
                break
        return roots
else:
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
