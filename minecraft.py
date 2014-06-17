from flask import Flask, request, jsonify, render_template, current_app
app = Flask(__name__)

from ping import get_info, get_info_old
from mcquery import MCQuery
from helpers import parse_server_data, parse_old_data, parse_query_data, format_date
from cache import get_cache_item, set_cache_item, get_stats
from hashlib import md5
from time import time
from exception import InvalidUsage
from functools import wraps
from raven.contrib.flask import Sentry

import requests
import socket

app.config.from_object('config')

sentry = Sentry(app)


# JSONP support for all methods :D
def jsonp(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


# Someone hasn't read the documentation...
@app.errorhandler(InvalidUsage)
@jsonp
def handle_invalid_usage(error):
    return jsonify(error.to_dict())


# I probably broke something / don't have good error handling
@app.errorhandler(500)
@jsonp
def err_500(error):
    return jsonify({
        "status": "error"
    })


# Documentation!
@app.route('/')
def index():
    return render_template('index.html')


# Documentation, for non programmers
@app.route('/tutorial')
def tutorial():
    return render_template('howto.html')


# This number goes up way too fast :p
@app.route('/stats')
@jsonp
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


# Versions of Minecraft
@app.route('/versions')
@jsonp
def get_versions():
    try:
        versions = get_cache_item('versions')
    except:
        json = requests.get(
            'http://s3.amazonaws.com/Minecraft.Download/versions/versions.json').json()
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
        output['latest'][version]['niceTime'] = format_date(
            bykey[versions['latest'][version]])

    return jsonify(output)


# Really what this API is for, fetching Minecraft server statuses :p
@app.route('/server/status')
@jsonp
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

    olderServer = False

    if not result:
        result = {}
        result['time'] = time()

        try:
            result['value'] = get_info(ip, port)
        except ValueError:  # Can't decode it as JSON, it's probably an old server
            olderServer = True
        except socket.error:  # Can't connect, this can sometimes be an old server issue
            olderServer = True
        except:  # Server is probably down
            result['value'] = False

        if olderServer:
            print 'test'
            try:
                result['value'] = get_info_old(ip, port)
                result['value']['old'] = True
            except:  # If we still can't get information, it's probably not a Minecraft server
                result['value'] = False

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

    if olderServer or 'old' in result['value']:
        result = parse_old_data(result)
    else:
        result = parse_server_data(result, favicon, players)

    return jsonify(result)


@app.route('/server/info')
@jsonp
def server_info():
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
    m.update('q%s%s' % (ip, port))
    m = m.hexdigest()

    try:
        result = get_cache_item(m)
    except:
        result = False

    if not result:
        result = {}
        result['time'] = time()

        try:
            result['value'] = MCQuery(ip, port).full_stat()
        except Exception as e:
            print e
            result['value'] = False

        print result

        set_cache_item(m, result['value'])

    if not result['value']:
        return jsonify({
            'status': 'success',
            'online': False
        })

    return jsonify(parse_query_data(result))


if __name__ == '__main__':
    app.run()
