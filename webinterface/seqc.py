import os
import json
import logging

import madmagia.sequence
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
        'sub': sec.sub.replace('\\n', '\n'),
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
        logging.exception(e)
        return 'fail'


@app.get_async('/seqc/get/')
def get_sections(r):
    path = os.path.join(r.args['path'], 'sequence.txt')
    logging.info('Load from %s', path)
    try:
        with open(path, 'r') as f:
            sections = madmagia.sequence.parse(
                [unicode(ln, 'utf-8') for ln in f.readlines()], False)[0]
        return [_dump_section(s) for s in sections]
    except madmagia.sequence.ParseError, e:
        logging.exception(e)
        logging.error('Error at line %d', e.linenum)
    except StandardError, e:
        logging.exception(e)
    return [_dump_section(madmagia.sequence.Section(0, ':begin'))]


def _write_segment(f, seg):
    print >> f, '   ', seg['epnum'], seg['start'], seg['duration']
    for fname, fargs in seg['filters']:
        print >> f, ('    :%s' % fname), fargs or ''


def _write_section(f, sec):
    if sec['name'] != ':begin':
        print >> f, ':section', sec['start'], sec['name'].encode(
            'utf-8'), sec.get('sub', '').replace('\n', '\\n').encode('utf-8')
    for s in sec['segments']:
        _write_segment(f, s)
    print >> f, ''


@app.post_async('/seqc/save')
def save_sequences(r):
    path = os.path.join(r.form['path'], 'sequence.txt')
    logging.info('Save to %s', path)
    with open(path, 'w') as f:
        for s in json.loads(r.form['sections']):
            _write_section(f, s)
