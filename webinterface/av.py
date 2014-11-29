import os
import flask
import tempfile
import urllib

import madmagia.audio_slice
import madmagia.video_slice
import madmagia.files
import app


def _temp_dir(path):
    if isinstance(path, unicode):
        path = path.encode('utf-8')
    d = os.path.join(
        app.temp_dir, urllib.quote(path.replace('\\', '/')).replace(
            '/', '%2F').replace('%', '.'))
    app.sure_mkdir(d)
    return d


@app.get_async('/info/len/')
def media_len(r):
    path = r.args['path']
    try:
        return madmagia.audio_slice.audio_len(path)
    except StandardError:
        return -1


@app.get_async('/info/videols/')
def video_map(r):
    path = r.args['path']
    try:
        return [{'epnum': k, 'path': v} for k, v in
                madmagia.files.input_videos(
                    path, ['mkv', 'mov', 'mp4']).iteritems()]
    except StandardError:
        return []

@app.post_async('/frame/gen')
def gen_frame(r):
    epnum = r.form['epnum']
    time = float(r.form['time'])
    return madmagia.video_slice.save_frame_to(
        time, r.form['source_path'],
        os.path.join(_temp_dir(r.form['output_path']), '%s_%f.png' % (epnum, time)),
        (480, 270))

@app.app.route('/frame/', methods=['GET'])
def view_frame():
    return flask.send_file(flask.request.args['path'].encode('utf-8'))

@app.app.route('/frame/loading', methods=['GET'])
def frame_loading():
    return flask.send_file(os.path.join(app.static_dir, 'loading.jpg'))

@app.app.route('/video/', methods=['GET'])
def view_video():
    return flask.send_file(flask.request.args['path'].encode('utf-8'))
