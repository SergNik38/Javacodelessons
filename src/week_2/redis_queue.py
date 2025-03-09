import json
import redis


class RedisQueue:
    def __init__(self, queue_name="default_queue", host="localhost", port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.queue_name = queue_name

    def publish(self, msg: dict):
        message = json.dumps(msg)
        self.redis_client.rpush(self.queue_name, message)

    def consume(self) -> dict:
        message = self.redis_client.lpop(self.queue_name)
        if message is None:
            raise ValueError("Очередь пуста")
        return json.loads(message)


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
