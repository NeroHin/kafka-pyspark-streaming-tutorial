import json, random, time
from kafka import KafkaProducer

BOOTSTRAP = "localhost:29092"
STRATEGIES = ["A", "B", "C"]

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8")
)

def gen_msg(strategy: str) -> tuple[str, dict]:
    key = f"user-{random.randint(1, 5)}"
    payload = {
        "strategy": strategy,
        "value": random.randint(1, 100),
        "ts": int(time.time() * 1000)
    }
    return key, payload

try:
    while True:
        for s in STRATEGIES:
            k, v = gen_msg(s)
            producer.send(f"{s}_input", key=k, value=v)
        producer.flush()
        time.sleep(1)          # 每秒三筆
except KeyboardInterrupt:
    print("Stopped producer.")