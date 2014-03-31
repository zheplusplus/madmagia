import os
import tempfile
import subprocess

_vfilters = dict()


def _vfilter(f):
    _vfilters[f.__name__[1:]] = f
    return f


@_vfilter
def _repeatframe(i, seg, source_file, tmp_name_id, tmp_output):
    image = os.path.join(tempfile.gettempdir(),
                         'tmp_' + str(i) + '_' + tmp_name_id + '.png')
    if save_frame(source_file, seg.start, image):
        raise ValueError('process fail at ' + str(i))
    tmp_file = tmp_output + '_repeat_frame.mp4'
    p = subprocess.Popen([
        'avconv',
        '-loop', '1',
        '-i', image,
        '-vcodec', 'libx264',
        '-tune', 'stillimage',
        '-t', str(seg.duration),
        '-vf', 'scale=640:360',
        tmp_file])
    p.wait()
    if p.returncode != 0:
        raise ValueError('process fail at ' + str(i))
    return tmp_file


@_vfilter
def _hflip(i, seg, source_file, tmp_name_id, tmp_output):
    tmp_file = tmp_output + '_hflip.mp4'
    p = subprocess.Popen([
        'avconv',
        '-i', tmp_output,
        '-vcodec', 'libx264',
        '-vf', 'hflip',
        tmp_file])
    p.wait()
    if p.returncode != 0:
        raise ValueError('process fail at ' + str(i))
    return tmp_file


def save_frame(source_file, time, output_file):
    p = subprocess.Popen([
        'avconv',
        '-ss', str(time),
        '-i', source_file,
        '-vsync', '1',
        '-t', '0.01',
        output_file], stderr=subprocess.PIPE)
    errmsg = p.communicate()[1]
    return p.returncode != 0 and 'filename number 2 from pattern' not in errmsg


def from_segments(source_files, tmp_name_id, segments):
    tmp_files = []
    for i, seg in enumerate(segments):
        tmp_file = os.path.join(tempfile.gettempdir(), tmp_name_id + str(i))
        source_file = source_files[seg.epnum - 1]
        p = subprocess.Popen([
            'avconv',
            '-ss', str(seg.start),
            '-i', source_file,
            '-t', str(seg.duration),
            '-vf', 'scale=640:360',
            '-f', 'mp4',
            '-vcodec', 'libx264',
            '-an',
            tmp_file])
        p.wait()
        if p.returncode != 0:
            raise ValueError('process fail at ' + str(i))

        for vfilter in seg.filters:
            if vfilter not in _vfilters:
                raise ValueError('No such filter: ' + vfilter)
            tmp_file = _vfilters[vfilter](
                i, seg, source_file, tmp_name_id, tmp_file)

        if seg.subt is not None:
            p = subprocess.Popen([
                'avconv',
                '-i', tmp_file,
                '-vf', '''drawtext=fontfile='/usr/share/fonts/truetype/''' +
                       """ttf-dejavu/DejaVuSans.ttf':text='""" + seg.subt +
                       """':x=0:y=0:fontsize=36:fontcolor=black""",
                '-vcodec', 'libx264',
                tmp_file + '.sub.mp4'])
            p.wait()
            if p.returncode != 0:
                raise ValueError('process fail at ' + str(i))
            tmp_file + '.sub.mp4'
        tmp_files.append(tmp_file)
    output_video = os.path.join(tempfile.gettempdir(), tmp_name_id + '.mp4')
    p = subprocess.Popen([
        'mencoder', '-ovc', 'x264', '-o', output_video] +
        tmp_files)
    p.wait()
    if p.returncode != 0:
        raise ValueError('fail')
    return output_video
