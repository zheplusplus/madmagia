import os
import types
from cStringIO import StringIO
import functools
from cgi import parse_qs
import json
import flask
import werkzeug.exceptions
import tempfile

from madmagia.config import config
from madmagia.pathutil import PATH_ENCODING


def sure_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

base_dir = os.path.dirname(__file__)
static_dir = os.path.join(base_dir, 'static')
temp_dir = os.path.join(tempfile.gettempdir(), 'madmagia')
sure_mkdir(temp_dir)
app = flask.Flask('MadMagia', static_folder=static_dir)
app.debug = 1
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

bin_dir = os.path.join(base_dir, 'bin')
config['avconv'] = os.path.join(bin_dir, 'ffmpeg', 'bin', 'avconv')
config['mencoder'] = os.path.join(bin_dir, 'MPlayer', 'mencoder')
#config['avconv'] = 'avconv'


def path(p):
    if isinstance(p, unicode):
        return p.encode(PATH_ENCODING)
    return str(p)


# http://stackoverflow.com/a/11163649
class _WSGICopyBody(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0

        body = environ['wsgi.input'].read(length)
        environ['body_copy'] = body
        environ['wsgi.input'] = StringIO(body)

        return self.application(environ, self._sr_callback(start_response))

    def _sr_callback(self, start_response):
        def callback(status, headers, exc_info=None):
            start_response(status, headers, exc_info)
        return callback

app.wsgi_app = _WSGICopyBody(app.wsgi_app)


def json_result(obj, status_code=200):
    r = flask.Response(json.dumps(obj), mimetype='application/json')
    r.status_code = status_code
    return r


def lazyprop(f):
    attr_name = '_l_' + f.__name__

    @property
    def g(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, f(self))
        return getattr(self, attr_name)

    return g


def strip_irregular_space(s):
    return s.replace('\t', '').replace('\r', '')


class Request(object):
    def __init__(self):
        self.request = flask.request
        self.args = flask.request.args
        self.session = flask.session

    @lazyprop
    def post_body(self):
        return self.request.environ['body_copy']

    @lazyprop
    def post_body_text(self):
        return unicode(strip_irregular_space(self.post_body), 'utf-8')

    @lazyprop
    def post_json(self):
        return json.loads(self.post_body_text)

    @lazyprop
    def form(self):
        try:
            return {k: unicode(strip_irregular_space(v[0]), 'utf-8')
                    for k, v in parse_qs(self.post_body).iteritems()}
        except (ValueError, TypeError, AttributeError, LookupError):
            return dict()


def route_async(uri, method):
    def wrapper(f):
        @app.route(uri, methods=[method])
        @functools.wraps(f)
        def g(*args, **kwargs):
            return json_result(f(Request(), *args, **kwargs))
        return g
    return wrapper

get_async = lambda uri: route_async(uri, 'GET')
post_async = lambda uri: route_async(uri, 'POST')
