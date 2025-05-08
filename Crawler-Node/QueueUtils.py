import redis
import json

# ✅ Hardcoded Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB   = 0

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def send_task(queue_name, data):
    """
    Push JSON-encoded data to a Redis queue.
    """
    try:
        redis_client.rpush(queue_name, json.dumps(data))
        print(f"[QueueUtils] Task pushed to '{queue_name}'")
    except Exception as e:
        print(f"[QueueUtils] Failed to send task to '{queue_name}': {e}")

def receive_task(queue_name, block=True, timeout=0):
    """
    Receive a task from a Redis queue.
    - If block=True: blocks until a message is available.
    - If block=False: non-blocking, returns immediately.
    """
    try:
        if block:
            result = redis_client.blpop(queue_name, timeout=timeout)
        else:
            result = redis_client.lpop(queue_name)

        if result:
            _, raw = result if block else ("", result)
            return json.loads(raw)
    except Exception as e:
        print(f"[QueueUtils] Failed to receive task from '{queue_name}': {e}")

    return None
