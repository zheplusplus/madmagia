import os
import flask
import tempfile
import urllib
import json

import madmagia.audio_slice
import madmagia.video_slice
import madmagia.avmerge
import madmagia.sequence
import madmagia.files
from madmagia.config import logger
import app


def _temp_dir(path):
    path = app.path(path)
    d = os.path.join(
        app.temp_dir, urllib.quote(path.replace('\\', '/')).replace(
            '/', '%2F').replace('%', '.'))
    app.sure_mkdir(d)
    return d


@app.get_async('/info/len/')
def media_len(r):
    try:
        return madmagia.audio_slice.audio_len(app.path(r.args['path']))
    except StandardError, e:
        logger.exception(e)
        return -1


@app.get_async('/info/videols/')
def video_map(r):
    path = r.args['path']
    try:
        return [{'epnum': k, 'path': v} for k, v in
                madmagia.files.input_videos(
                    path, ['mkv', 'mov', 'mp4']).iteritems()]
    except StandardError, e:
        logger.exception(e)
        return []


@app.post_async('/audio/slice')
def audio_slice(r):
    path = app.path(r.form['file'])
    start = float(r.form['start'])
    duration = float(r.form['duration'])
    output_dir = _temp_dir(r.form['output_dir'])
    try:
        return madmagia.audio_slice.slice(path, start, start + duration,
                                          output_dir)
    except StandardError, e:
        logger.exception(e)
        return []


@app.app.route('/audio/', methods=['GET'])
def listen_audio():
    return flask.send_file(app.path(flask.request.args['path']))


@app.post_async('/video/slice')
def video_slice(r):
    time_start = float(r.form['start'])
    time_end = float(r.form['end'])
    audio_file = r.form['audio']
    segments = [madmagia.sequence.Segment(**s)
                for s in json.loads(r.form['segments'])]
    input_files = madmagia.files.input_videos(
        r.form['video_dir'], ['mkv', 'mov', 'mp4'])
    output_dir = _temp_dir(r.form['output_dir'])
    merged_video = madmagia.video_slice.merge_segments(
        madmagia.video_slice.slice_segments(
            input_files, segments, output_dir), output_dir)
    audio_seg = madmagia.audio_slice.slice(
        audio_file, time_start, time_end, output_dir)
    return madmagia.avmerge.avmerge(
        audio_seg, merged_video, os.path.join(output_dir, 'output.mp4'))


@app.post_async('/frame/gen')
def gen_frame(r):
    epnum = r.form['epnum']
    time = float(r.form['time'])
    return madmagia.video_slice.save_frame_to(
        time, app.path(r.form['source_path']),
        os.path.join(_temp_dir(r.form['output_path']),
                     '%s_%f.png' % (epnum, time)),
        (480, 270))


@app.app.route('/frame/', methods=['GET'])
def view_frame():
    return flask.send_file(app.path(flask.request.args['path']))


@app.app.route('/frame/loading', methods=['GET'])
def frame_loading():
    return flask.send_file(os.path.join(app.static_dir, 'loading.jpg'))


@app.app.route('/video/', methods=['GET'])
def view_video():
    return flask.send_file(app.path(flask.request.args['path']))