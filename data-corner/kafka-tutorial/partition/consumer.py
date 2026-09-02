from confluent_kafka import Consumer
import json
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-workers',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['orders'])

totals = {}

while True:
    message = consumer.poll(1)

    if message is None:
        continue
    if message.error():
        print(f"Error: {message.error()}")
        continue

    order = json.loads(message.value().decode())
    customer_id = order['customer_id']

    if customer_id in totals:
        totals[customer_id] += order['amount']
    else:
        totals[customer_id] = order['amount']

    print(f"Customer: {customer_id}, Total Amount: {totals[customer_id]}")
    print(f"Partition: {message.partition()}, Offset: {message.offset()}")
