import os
import flask
import tempfile
import urllib
import json
import time

import madmagia.audio_slice
import madmagia.video_slice
import madmagia.avmerge
import madmagia.sequence
import madmagia.files
import madmagia.shell
from madmagia.config import logger, config
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
                madmagia.files.input_videos(path, ['mkv']).iteritems()]
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
    config['bitrate'] = '1.6M'
    config['resolution'] = '800:450'
    segment = madmagia.sequence.Segment(**json.loads(r.form['segment']))
    input_files = madmagia.files.input_videos(r.form['video_dir'], ['mkv'])
    output_dir = _temp_dir(r.form['output_dir'])
    try:
        return madmagia.video_slice.slice_segment(0, segment, input_files,
                                                  output_dir)
    except madmagia.shell.ShellError:
        return ''


@app.post_async('/video/merge')
def video_merge(r):
    time_start = float(r.form['start'])
    time_end = float(r.form['end'])
    audio_file = r.form['audio']
    output_dir = _temp_dir(r.form['output_dir'])
    merged_video = madmagia.video_slice.merge_segments(
        json.loads(r.form['segments']), output_dir)
    audio_seg = madmagia.audio_slice.slice(
        audio_file, time_start, time_end, output_dir)
    return madmagia.avmerge.avmerge(
        audio_seg, merged_video, os.path.join(
            output_dir, 'output-%d.mp4' % time.time()), 'libx264')


@app.post_async('/video/slice_export')
def video_slice_export(r):
    config['bitrate'] = '16M'
    config['resolution'] = '1280:720'
    segment = madmagia.sequence.Segment(**json.loads(r.form['segment']))
    input_files = madmagia.files.input_videos(r.form['video_dir'], ['mkv'])
    output_dir = _temp_dir(r.form['output_dir']) + '.export'
    app.sure_mkdir(output_dir)
    return madmagia.video_slice.slice_segment(0, segment, input_files,
                                              output_dir)


@app.post_async('/video/merge_export')
def video_merge_export(r):
    time_start = float(r.form['start'])
    time_end = float(r.form['end'])
    audio_file = r.form['audio']
    output_dir = r.form['output_dir']
    merged_video = madmagia.video_slice.merge_segments(
        json.loads(r.form['segments']), output_dir)
    audio_seg = madmagia.audio_slice.slice(
        audio_file, time_start, time_end, output_dir)
    return madmagia.avmerge.avmerge(
        audio_seg, merged_video, os.path.join(
            output_dir, 'output-%d.mp4' % time.time()))


@app.post_async('/frame/gen')
def gen_frame(r):
    epnum = r.form['epnum']
    time = float(r.form['time'])
    try:
        return madmagia.video_slice.save_frame_to(
            time, app.path(r.form['source_path']),
            os.path.join(_temp_dir(r.form['output_path']),
                         '%s_%f.png' % (epnum, time)),
            (480, 270))
    except madmagia.shell.ShellError:
        return ''


@app.app.route('/frame/', methods=['GET'])
def view_frame():
    return flask.send_file(app.path(flask.request.args['path']))


@app.app.route('/frame/loading', methods=['GET'])
def frame_loading():
    return flask.send_file(os.path.join(app.static_dir, 'loading.jpg'))


@app.app.route('/video/', methods=['GET'])
def view_video():
    return flask.send_file(app.path(flask.request.args['path']))
