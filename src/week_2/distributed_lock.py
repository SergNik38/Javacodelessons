import time
from datetime import datetime, timedelta

import redis


def single(max_processing_time: timedelta):
    def decorator(func):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        lock_key = f"lock:{func.__module__}:{func.__name__}"

        def wrapper(*args, **kwargs):
            if redis_client.setnx(lock_key, 1):
                redis_client.expire(lock_key, int(
                    max_processing_time.total_seconds()))
                try:
                    return func(*args, **kwargs)
                finally:
                    redis_client.delete(lock_key)
            else:
                raise RuntimeError("Function is already running")

        return wrapper
    return decorator


if __name__ == "__main__":
    @single(max_processing_time=timedelta(minutes=2))
    def process_transaction():
        time.sleep(2)
        print("Transaction processed")

    process_transaction()
