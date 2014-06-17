import arrow


def parse_server_data(data, favicon=False, players=True):
    result = {}

    time = data['time']
    data = data['value']

    result['time'] = time
    result['status'] = 'success'

    result['online'] = True
    result['motd'] = data['description']

    result['players'] = {}

    result['players']['max'] = data['players']['max']
    result['players']['now'] = data['players']['online']

    if players:
        if 'sample' in data['players']:
            result['players']['sample'] = []

            for player in data['players']['sample']:
                result['players']['sample'].append(player)
        else:
            result['players']['sample'] = False

    if favicon:
        result['favicon'] = data['favicon']

    result['server'] = {}

    result['server']['name'] = data['version']['name']
    result['server']['protocol'] = data['version']['protocol']

    return result


def parse_old_data(data):
    result = {}

    time = data['time']
    data = data['value']

    result['time'] = time

    result['online'] = True
    result['motd'] = data['motd']
    result['status'] = 'success'

    result['players'] = {}

    result['players']['max'] = data['max_players']
    result['players']['now'] = data['players']

    result['server'] = {}

    result['server']['name'] = data['server_version']

    return result


def format_date(date):
    d = arrow.get(date)

    return d.humanize()
