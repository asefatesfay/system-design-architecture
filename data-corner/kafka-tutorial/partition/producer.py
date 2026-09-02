import hashlib
import json

from confluent_kafka import Producer

NUM_PARTITIONS = 3

def get_partition(key):
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % NUM_PARTITIONS

def on_delivery(err, msg):
    if err:
        print(f"ERROR: {err}")
    else:
        print(f"key={msg.key().decode()} → partition={msg.partition()}")

producer = Producer({'bootstrap.servers': 'localhost:9092'})
metadata = producer.list_topics('orders', timeout=10)
topic_metadata = metadata.topics['orders']
print(f"Topic error: {topic_metadata.error}")
for pid, p in topic_metadata.partitions.items():
    print(f"  Partition {pid}: leader={p.leader}, error={p.error}")
partitions = sorted(topic_metadata.partitions.keys())
NUM_PARTITIONS = len(partitions)

for i in range(100):
    order = {
        'order_id': i,
        'customer_id': f'customer_{i}',
        'amount': i * 100
    }
    key = str(order['customer_id'])
    producer.produce(
        'orders',
        key=key,
        value=json.dumps(order),
        partition=get_partition(key),
        callback=on_delivery
    )

producer.flush()
