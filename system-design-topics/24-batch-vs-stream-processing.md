# Batch vs Stream Processing

## Definition

**Batch Processing:** Process large volumes of data collected over a period of time (hours, days) in scheduled jobs.

**Stream Processing:** Process data continuously in real-time as it arrives (milliseconds, seconds).

## Comparison

| Aspect | Batch Processing | Stream Processing |
|--------|------------------|-------------------|
| **Latency** | Minutes to hours | Milliseconds to seconds |
| **Data Volume** | Large datasets | Continuous flow |
| **Use Case** | Historical analysis | Real-time decisions |
| **Examples** | Daily reports, ETL | Fraud detection, monitoring |
| **Complexity** | Simpler | More complex |
| **Cost** | Lower (scheduled) | Higher (always running) |

## Batch Processing

### Examples

**Hadoop MapReduce:**
```python
# Process 1TB of logs daily
input: access_logs_2026-02-08.txt (1 million records)
```
Run at 2 AM:
- Count requests per IP
- Analyze user patterns
- Generate report
Output: summary_2026-02-08.csv

Takes: 30 minutes ✓ (acceptable for daily report)
```

**Spark Batch:**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DailySales").getOrCreate()

# Read yesterday's sales
sales = spark.read.parquet("s3://sales/2026-02-08/")

# Aggregate by product
summary = sales.groupBy("product_id").agg({"amount": "sum"})

# Write report
summary.write.csv("s3://reports/sales_2026-02-08.csv")
```

**AWS Glue (ETL):**
```
Daily ETL pipeline:
1. Extract data from RDS (midnight)
2. Transform (clean, aggregate)
3. Load to Redshift
4. Takes: 1-2 hours
5. Analysts query in morning
```

### Use Cases

✅ **Payroll processing** (monthly)
✅ **Data warehouse ETL** (nightly)
✅ **Monthly reports** (billing, analytics)
✅ **Machine learning training** (daily model updates)
✅ **Log analysis** (historical patterns)

## Stream Processing

### Examples

**Apache Kafka Streams:**
```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> transactions = builder.stream("transactions");

// Detect fraud in real-time
transactions
  .filter((key, value) -> isSuspicious(value))
  .to("fraud-alerts");  // Alert immediately!

// Takes: <100ms ✓
```

**Apache Flink:**
```python
# Real-time trending hashtags
stream = env.add_source(KafkaSource("tweets"))

trending = stream
  .window_all(TumblingEventTimeWindows.of(Time.minutes(5)))
  .aggregate(CountHashtags())

trending.print()  # Updates every 5 minutes
```

**AWS Kinesis:**
```python
import boto3

kinesis = boto3.client('kinesis')

# Stream processing Lambda
def lambda_handler(event, context):
    for record in event['Records']:
        data = json.loads(base64.b64decode(record['kinesis']['data']))
        
        # Real-time analysis
        if data['temperature'] > 100:
            send_alert(data)  # Immediate alert!
```

### Use Cases

✅ **Fraud detection** (credit cards in real-time)
✅ **Monitoring/alerting** (server metrics, errors)
✅ **Recommendation engines** (personalize as user browses)
✅ **IoT sensor data** (factory equipment, smart homes)
✅ **Stock trading** (algorithmic trading, price alerts)
✅ **Real-time dashboards** (website analytics)

## Real-World Examples

### Netflix
**Batch:**
- Nightly: Generate personalized recommendations for all users
- Takes: Hours to process viewing history

**Stream:**
- Real-time: Update "Continue Watching" as user watches
- Real-time: Detect playback issues, adjust quality

### Uber
**Batch:**
- Daily: Analyze trip data, optimize pricing models
- Takes: Hours to process millions of trips

**Stream:**
- Real-time: Match drivers to riders (<1 second)
- Real-time: Surge pricing based on current demand
- Real-time: ETA calculations

### Twitter
**Batch:**
- Daily: Analyze tweet sentiment, trends over time
- Train ML models on historical data

**Stream:**
- Real-time: Trending topics (updates every minute)
- Real-time: Timeline updates (tweets appear instantly)
- Real-time: Spam detection

### Banking
**Batch:**
- End of day: Balance calculations, interest accrual
- Monthly: Generate statements

**Stream:**
- Real-time: Fraud detection (block suspicious transactions)
- Real-time: Account balance updates
- Real-time: Transaction notifications

## Lambda Architecture (Hybrid)

**Combine batch + stream for best of both worlds**

```
                Speed Layer (Stream)
                Real-time results
                Approximate
                    ↓
Input Data → ──────┴─────── → Merge → Query
                    ↑
                Batch Layer
                Accurate results
                Complete history
```

**Example: View counts**
```
Batch (every hour): Accurate count from database
Stream (real-time): Approximate count via increments

Display: batch_count (1 hour old) + stream_delta (real-time)
Result: Near real-time + eventually accurate ✓
```

## Technologies

### Batch Processing
- **Hadoop MapReduce** (distributed computing)
- **Apache Spark** (in-memory batch processing)
- **AWS Glue** (managed ETL)
- **Airflow** (workflow orchestration)

### Stream Processing
- **Apache Kafka** + Kafka Streams
- **Apache Flink** (stateful stream processing)
- **Apache Storm** (real-time computation)
- **AWS Kinesis** (managed streaming)
- **Spark Streaming** (micro-batches)

## Choosing Batch vs Stream

```
Choose Batch if:
✅ Latency not critical (hours acceptable)
✅ Processing large historical data
✅ Complex transformations (joins, aggregations)
✅ Cost-sensitive (run only when needed)

Choose Stream if:
✅ Need real-time results (seconds)
✅ Continuous data flow (logs, events, sensors)
✅ Time-sensitive decisions (fraud, monitoring)
✅ Latest data critical (dashboards, alerts)
```

## Micro-Batching (Middle Ground)

**Spark Streaming approach:**
```
Collect data in small batches (1-10 seconds)
Process each micro-batch
Near real-time (good enough for many use cases)
Simpler than pure streaming
```

## Best Practices

### Batch
✅ Schedule during low-traffic hours
✅ Partition data (process in parallel)
✅ Monitor job failures, implement retries
✅ Use snapshots/checkpoints for large jobs

### Stream
✅ Handle late-arriving data (watermarks)
✅ Implement back-pressure (don't overwhelm)
✅ Ensure exactly-once semantics
✅ Monitor lag (processing speed vs input speed)

## Interview Tips

**Q: "Batch vs Stream processing?"**

**A:** Batch processes large datasets periodically (hours), good for reports, analytics. Stream processes data continuously (milliseconds), good for fraud detection, monitoring. Batch is cheaper and simpler, stream is real-time but complex.

**Q: "Design a system to detect credit card fraud"**

**A:** Use stream processing (Kafka + Flink). Each transaction processed in real-time (<100ms). Check against fraud rules, ML model. Alert immediately if suspicious. Can't wait for batch processing (daily report too late).

**Q: "When would you use Lambda architecture?"**

**A:** When need both real-time results and accurate historical analysis. Example: Real-time dashboard (stream) + nightly reports (batch). View counts: Stream for real-time approximation, batch for accurate totals.

**Key Takeaway:** Batch for historical analysis, Stream for real-time decisions. Choose based on latency requirements!
