from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

from ping_server import get_info
from helpers import parse_server_data, format_date
from cache import get_cache_item, set_cache_item, get_stats
from hashlib import md5
from time import time
from exception import InvalidUsage

import requests


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/stats')
def stats():
    try:
        result = get_stats()
    except:
        result = 0

    if result is None:
        result = 0

    return jsonify({
        'stats': int(result)
    })


@app.route('/versions')
def get_versions():
    try:
        versions = get_cache_item('versions')
    except:
        json = requests.get('http://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
        set_cache_item('versions', json)

        versions = {}
        versions['time'] = time()
        versions['value'] = json

    output = {}

    output['status'] = 'success'
    output['versions'] = []
    output['time'] = versions['time']

    versions = versions['value']

    bykey = {}

    for version in versions['versions']:
        v = {}
        v['id'] = version['id']
        v['time'] = version['time']
        v['niceTime'] = format_date(version['time'])
        v['type'] = version['type']

        output['versions'].append(v)

        bykey[version['id']] = version['time']

    output['latest'] = {}

    for version in versions['latest']:
        output['latest'][version] = {}

        output['latest'][version]['id'] = versions['latest'][version]
        output['latest'][version]['time'] = bykey[versions['latest'][version]]
        output['latest'][version]['niceTime'] = format_date(bykey[versions['latest'][version]])

    return jsonify(output)

@app.route('/server/status')
def server_status():
    ip = request.args.get('ip')

    if not ip:
        raise InvalidUsage('no ip')

    port = request.args.get('port')

    if port is None:
        port = 25565
    else:
        try:
            port = int(port)
        except:
            raise InvalidUsage('invalid port')

    m = md5()
    m.update('%s%s' % (ip, port))
    m = m.hexdigest()

    try:
        result = get_cache_item(m)
    except:
        result = False

    if not result:
        result = {}
        result['time'] = time()
        result['value'] = get_info(ip, port)

        set_cache_item(m, result['value'])

    if not result['value']:
        return jsonify({
            'status': 'success',
            'online': False
        })

    if request.args.get('favicon') is None or request.args.get('favicon') == 'false':
        favicon = False
    else:
        favicon = True

    if request.args.get('players') is not None or request.args.get('players') == 'true':
        players = True
    else:
        players = False

    return jsonify(parse_server_data(result, favicon, players))


@app.route('/server/info')
def server_info():
    return 'nyi'

if __name__ == "__main__":
    app.run(debug=True, host='::')
