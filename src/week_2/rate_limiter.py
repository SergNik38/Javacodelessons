import random
import time
import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(
        self, max_requests=5, window_seconds=3, host="localhost", port=6379, db=0
    ):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key = "rate_limiter"

    def test(self) -> bool:
        current_time = time.time()
        self.redis_client.lpush(self.key, current_time)
        self.redis_client.ltrim(self.key, 0, self.max_requests - 1)
        self.redis_client.expire(self.key, self.window_seconds)

        oldest_request = float(self.redis_client.lindex(self.key, -1) or 0)
        return (
            len(self.redis_client.lrange(self.key, 0, -1)) < self.max_requests
            or current_time - oldest_request >= self.window_seconds
        )


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
