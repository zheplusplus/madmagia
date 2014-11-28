import os
import json

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
        'sub': sec.sub,
        'segments': [_dump_segment(s) for s in sec.segments],
    }


@app.get_async('/seqc/get/')
def get_sections(r):
    path = r.args['path']
    try:
        with open(os.path.join(path, 'sequence.txt'), 'r') as f:
            sections = madmagia.sequence.parse(f.readlines())[0]
        return [_dump_section(s) for s in sections]
    except StandardError:
        return []


def _write_segment(f, seg):
    print >> f, '   ', seg['epnum'], seg['start'], seg['duration']
    for fname, fargs in seg['filters']:
        print >> f, ('    :%s' % fname), fargs or ''


def _write_section(f, sec):
    if sec['name'] != ':begin':
        print >> f, ':section', sec['start'], sec['name'], sec.get('sub', '')
    for s in sec['segments']:
        _write_segment(f, s)
    print >> f, ''


@app.post_async('/seqc/save')
def save_sequences(r):
    with open(os.path.join(r.form['path'], 'sequence.txt'), 'w') as f:
        [_write_section(f, s) for s in json.loads(r.form['sections'])]
