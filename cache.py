import redis
import pickle
import config
from time import time

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
CACHE_TIMEOUT = 60 * 5


def set_cache_item(key, value):
    the_item = {}

    the_item['value'] = value
    the_item['time'] = time()

    r.set(key, pickle.dumps(the_item))

    r.expire(key, CACHE_TIMEOUT)


def get_cache_item(key):
    the_item = r.get(key)

    r.incr('mcapi')

    if the_item is None:
        return None

    return pickle.loads(the_item)


def get_stats():
    return r.get('mcapi')
