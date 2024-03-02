import redis


def get_redis():
    with redis.Redis(decode_responses=True) as r:
        yield r
