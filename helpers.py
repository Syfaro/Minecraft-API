def parse_server_data(data, favicon=False, players=True):
    result = {}

    time = data['time']
    data = data['value']

    result['time'] = time

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
