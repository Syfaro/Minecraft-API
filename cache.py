import fakeredis
import json
from time import time

r = fakeredis.FakeStrictRedis()
CACHE_TIMEOUT = 60 * 5


def set_cache_item(version, key, value):
    the_item = {}

    the_item['value'] = value
    the_item['time'] = time()

    r.set('%s:%s' % (version, key), json.dumps(the_item))
    r.expire('%s:%s' % (version, key), CACHE_TIMEOUT)


def get_cache_item(version, key):
    the_item = r.get('%s:%s' % (version, key))

    return json.loads(the_item)
