import redis
import os


def getRedisClient():
    return redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
