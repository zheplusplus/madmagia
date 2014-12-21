import os
import json

import madmagia.sequence
from madmagia.config import logger
import app


def _dump_segment(seg):
    return {
        'epnum': seg.epnum,
        'start': seg.start,
        'duration': seg.duration,
        'filters': seg.filters,
    }


def _dump_section(sec):
    return {
        'name': sec.name,
        'start': sec.start,
        'sub': sec.sub,
        'segments': [_dump_segment(s) for s in sec.segments],
    }


@app.post_async('/seqc/touch')
def touch_sequence_file(r):
    path = os.path.join(r.form['path'], 'sequence.txt')
    if os.path.isfile(path):
        return 'ok'
    try:
        with open(path, 'a+'):
            return 'ok'
    except StandardError, e:
        logger.exception(e)
        return 'fail'


@app.get_async('/seqc/get/')
def get_sections(r):
    path = os.path.join(r.args['path'], 'sequence.txt')
    logger.info('Load from %s', path)
    try:
        with open(path, 'r') as f:
            sections = madmagia.sequence.parse(
                [unicode(ln, 'utf-8') for ln in f.readlines()], False)[0]
        return [_dump_section(s) for s in sections]
    except madmagia.sequence.ParseError, e:
        logger.exception(e)
        logger.error('Error at line %d', e.linenum)
    except StandardError, e:
        logger.exception(e)
    return [_dump_section(madmagia.sequence.Section(0, ':begin'))]


def _write_segment(f, seg):
    print >> f, '   ', seg['epnum'], seg['start'], seg['duration']
    for fname, fargs in seg['filters']:
        print >> f, ('    :%s' % fname), fargs or ''


def _write_section(f, sec):
    if sec['name'] != ':begin':
        print >> f, ':section', sec['start'], sec['name'].encode(
            'utf-8'), sec.get('sub', '')
    for s in sec['segments']:
        _write_segment(f, s)
    print >> f, ''


@app.post_async('/seqc/save')
def save_sequences(r):
    path = os.path.join(r.form['path'], 'sequence.txt')
    logger.info('Save to %s', path)
    with open(path, 'w') as f:
        [_write_section(f, s) for s in json.loads(r.form['sections'])]
