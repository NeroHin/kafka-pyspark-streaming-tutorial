import json, random, time
from kafka import KafkaProducer


BOOTSTRAP = "localhost:9092"
STRATEGIES = ["A", "B", "C", "D"]

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8")
)

def gen_msg(strategy: str) -> tuple[str, dict]:
    key = f"user-{random.randint(1, 1000)}"
    payload = {
        "strategy": strategy,
        "value": random.randint(1, 100),
        "ts": int(time.time() * 1000)
    }
    return key, payload

try:
    while True:
        # 每秒只生成一個使用者 key
        key = f"user-{random.randint(1, 1000)}"
        for s in STRATEGIES:
            # 為每個策略使用相同的 key
            payload = {
                "strategy": s,
                "value": random.randint(1, 100),
                "ts": int(time.time() * 1000)
            }
            producer.send(f"{s}_input", key=key, value=payload)
        producer.flush()
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped producer.")