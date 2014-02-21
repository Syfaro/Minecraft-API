import fakeredis
import json
from time import time

r = fakeredis.FakeStrictRedis()
CACHE_TIMEOUT = 60 * 5


def set_cache_item(key, value):
    the_item = {}

    the_item['value'] = value
    the_item['time'] = time()

    r.set(key, json.dumps(the_item))
    r.expire(key, CACHE_TIMEOUT)


def get_cache_item(key):
    the_item = r.get(key)

    r.incr('mcapi')

    return json.loads(the_item)


def get_stats():
	return r.get('mcapi')