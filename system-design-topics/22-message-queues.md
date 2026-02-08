# Message Queues

## Definition

**Message Queues** enable asynchronous communication between services by storing messages until they can be processed, decoupling producers (senders) from consumers (receivers).

## How It Works

```
Producer → Queue → Consumer

Producer: Create job → Send to queue → Continue immediately ✅
Queue: Store message reliably
Consumer: Pull message → Process → Acknowledge → Delete
```

## Real-World Examples

### Amazon SQS (Simple Queue Service)
```python
import boto3

sqs = boto3.client('sqs')

# Send message
sqs.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    MessageBody='Process order #12345'
)

# Receive and process
messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
for message in messages['Messages']:
    # Process message
    process_order(message['Body'])
    
    # Delete after processing
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
```

### RabbitMQ
**Most popular open-source message broker**

```python
import pika

# Publisher
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='tasks')
channel.basic_publish(exchange='', routing_key='tasks', body='Task data')

# Consumer
def callback(ch, method, properties, body):
    print(f"Processing: {body}")
    # Simulate work
    process_task(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='tasks', on_message_callback=callback)
channel.start_consuming()
```

### Apache Kafka
**High-throughput distributed streaming**

```python
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('orders', b'Order #12345')

# Consumer
consumer = KafkaConsumer('orders', bootstrap_servers=['localhost:9092'])
for message in consumer:
    process_order(message.value)
```

**Used by:** LinkedIn, Uber, Netflix, Airbnb

### Redis Queue (Bull, BullMQ)
```javascript
const Queue = require('bull');
const emailQueue = new Queue('emails');

// Add job
await emailQueue.add({
  to: 'user@example.com',
  subject: 'Welcome!',
  body: 'Thanks for signing up'
});

// Process jobs
emailQueue.process(async (job) => {
  await sendEmail(job.data);
});
```

## Use Cases

### 1. Email Sending (Asynchronous)
```
User signs up → Add email job to queue → Return "success" immediately ✅
Background worker → Send email
User doesn't wait!
```

### 2. Image Processing
```
User uploads image → Queue: resize, optimize, generate thumbnails
Return quickly, process in background
```

### 3. Order Processing (E-commerce)
```
Order created → Queue:
1. Charge payment
2. Update inventory
3. Send confirmation email
4. Notify shipping

Each step processed reliably
```

### 4. Log Processing
```
Application logs → Queue → Aggregation → Analytics
Handles bursts, prevents data loss
```

### 5. Microservices Communication
```
Service A → Queue → Service B
Loose coupling, resilient to failures
```

## Queue Patterns

### 1. Work Queue (Competing Consumers)
```
Producer → Queue → [Worker1, Worker2, Worker3]
Each message processed by one worker
Load balanced automatically
```

### 2. Pub/Sub (Fan-out)
```
Publisher → Topic → [Subscriber1, Subscriber2, Subscriber3]
Each subscriber gets copy of message
Event broadcasting
```

### 3. Priority Queue
```
High priority jobs processed first
Critical tasks jump the queue
```

### 4. Delayed Queue
```
Schedule jobs for future
Example: Send reminder email in 7 days
```

## Benefits

✅ **Asynchronous processing** (don't block users)
✅ **Decoupling** (services independent)
✅ **Load leveling** (handle bursts)
✅ **Reliability** (retry failed jobs)
✅ **Scalability** (add more workers)

## Message Queue vs Database

| Feature | Message Queue | Database |
|---------|---------------|----------|
| Purpose | Async communication | Data storage |
| Retention | Until processed | Permanent |
| Access pattern | FIFO/priority | Random access |
| Guaranteed delivery | Yes (ack required) | N/A |

## Best Practices

✅ **Idempotent consumers** (handle duplicates)
✅ **Dead letter queue** (failed messages)
✅ **Monitor queue length** (alert on backlog)
✅ **Set message TTL** (expire old messages)

**Key Takeaway:** Message queues enable asynchronous, scalable, and reliable communication between services!
