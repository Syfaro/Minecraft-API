from flask import Flask, request, jsonify
app = Flask(__name__)

from ping_server import get_info
from helpers import parseServerStatus
from cache import get_cache_item, set_cache_item
from hashlib import md5
from time import time


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)

        self.message = message

        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message

        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.route("/")
def index():
    return "Hello, world!"


@app.route('/server/status')
def server_status():
    ip = request.args.get('ip')

    if not ip:
        raise InvalidUsage('no ip')

    if request.args.get('port') is None:
        port = 25565
    else:
        port = int(request.args.get('port'))

    m = md5()
    m.update('%s%s' % (ip, port))
    m = m.hexdigest()

    try:
        result = get_cache_item('1.3', m)
    except:
        result = False

    if not result:
        result = {}
        result['time'] = time()
        result['value'] = get_info(ip, port)

        set_cache_item('1.3', m, result['value'])

    if not result['value']:
        return jsonify({
            'status': 'success',
            'online': False
        })

    if request.args.get('favicon') is None:
        favicon = False
    elif request.args.get('favicon') == 'false':
        favicon = False
    else:
        favicon = True

    if request.args.get('players') is None:
        players = True
    elif request.args.get('players') == 'false':
        players = False
    else:
        players = True

    return jsonify(parseServerStatus(result, favicon, players))


@app.route('/server/info')
def server_info():
    return 'nyi'

if __name__ == "__main__":
    app.run(debug=True, host='::')
