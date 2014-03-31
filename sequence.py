import re
import functools
import collections


class ParseError(ValueError):
    def __init__(self, message, linenum, content):
        ValueError.__init__(self, message)
        self.linenum = linenum + 1
        self.content = content


class Segment(object):
    def __init__(self, epnum, start, duration, subt):
        self.epnum = epnum
        self.start = start
        self.duration = duration
        self.subt = subt
        self.filters = []

    def add_filter(self, f):
        self.filters.append(f)


class Section(object):
    def __init__(self, start_time, name):
        self.start_time = start_time
        self.name = name
        self.segments = []

    def add(self, segment):
        self.segments.append(segment)


_ctrls = dict()

def _ctrl(f):
    _ctrls[f.__name__[1:]] = f
    return f


def _decl_filter(f):
    def g(i, arg, sections, section_names):
        try:
            last_segment = sections[-1].segments[-1]
        except IndexError:
            raise ParseError('No segment before filter', i, arg)
        last_segment.add_filter(f)
    _ctrls[f] = g

_decl_filter('repeatframe')
_decl_filter('hflip')

_SECTION_TIME_PATTERN = re.compile(
    r'^((?P<min>[0-9]+):)?(?P<sec>[0-9]+)(?P<mil>\.[0-9]{1,3})?$')


def parse_time(time_str):
    time_parts = _SECTION_TIME_PATTERN.match(time_str)
    if time_parts is None:
        return None

    time_parts = time_parts.groupdict()
    return (int(time_parts['min'] or 0) * 60 +
            int(time_parts['sec']) + float(time_parts['mil'] or 0))


@_ctrl
def _section(i, arg, sections, section_names):
    space = arg.find(' ')
    if space == -1:
        raise ParseError('Invalid section format', i, arg)
    start_time = parse_time(arg[:space])
    if start_time is None:
        raise ParseError('Invalid section time format', i, arg[:space])

    name = arg[space + 1:].strip()
    if '-' in name or ':' in name:
        raise ParseError('Invalid section name', i, name)
    if name in section_names:
        raise ParseError('Duplicated section name', i, name)
    section_names.add(name)

    sections.append(Section(start_time, name))


def _segment(line):
    parts = filter(None, line.split(' '))
    if len(parts) == 3:
        epnum, start, dur = parts
        subt = None
    else:
        epnum, start, dur, subt = parts
    start_time = parse_time(start)
    return Segment(int(epnum), start_time, float(dur), subt)


def parse(sequence):
    total_dur = 0
    sections = [Section(.0, ':begin')]
    section_names = set()

    for i, line in enumerate(sequence):
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue

        if line[0] == ':':
            space = line[1:].find(' ')
            if space == -1:
                space = len(line)
            ctrl = line[1:space + 1]
            if ctrl not in _ctrls:
                raise ParseError('Unknown control', i, ctrl)
            _ctrls[ctrl](i, line[space + 2:].strip(), sections, section_names)
            continue

        try:
            segment = _segment(line)
        except (LookupError, ValueError):
            raise ParseError('Invalid segment', i, line)
        total_dur += segment.duration
        sections[-1].add(segment)
    return sections, total_dur
