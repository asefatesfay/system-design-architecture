from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group-new',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['my_topic'])

while True:
    message = consumer.poll(1)
    if message is not None:
        print(f"Received: {message.value().decode('utf-8')}")
        print(message.offset())