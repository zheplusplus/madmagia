import os
import flask
import json

import app

index_html = os.path.join(app.base_dir, 'index.html')
projects_json = os.path.join(app.base_dir, 'projects.json')


@app.app.route('/', methods=['GET'])
def index():
    return flask.send_file(index_html)


@app.get_async('/projs')
def projects(r):
    try:
        with open(projects_json, 'r') as f:
            return json.loads(f.read())
    except (IOError, ValueError):
        return []


@app.post_async('/saveprojs')
def save_projects(r):
    with open(projects_json, 'w') as f:
        f.write(r.post_body)
