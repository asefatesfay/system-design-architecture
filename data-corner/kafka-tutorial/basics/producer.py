from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092'})

while True:
    message = input("Enter a message to send to Kafka (or 'exit' to quit): ")
    if message.lower() == 'exit':
        break
    producer.produce('my_topic', value=message)
    producer.flush()
    print(f"Sent: {message}")