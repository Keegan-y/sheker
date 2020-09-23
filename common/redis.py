from redis import StrictRedis

from config import REDIS_HOST, REDIS_PORT

redis_client = StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
