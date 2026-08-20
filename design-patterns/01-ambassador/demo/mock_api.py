"""
Mock API Server for testing Ambassador pattern
Simulates an unreliable external API with:
- Random failures (500 errors)
- Random slow responses
- Rate limiting
"""

from flask import Flask, request, jsonify
import random
import time
from datetime import datetime

app = Flask(__name__)

# Configuration
FAILURE_RATE = 0.3  # 30% of requests fail on first attempt
SLOW_RESPONSE_RATE = 0.2  # 20% of responses are slow
SLOW_RESPONSE_DELAY = 2  # seconds

# Tracking
request_count = 0
failure_count = 0


@app.route('/charge', methods=['POST'])
def charge():
    """Payment endpoint with random failures"""
    global request_count, failure_count
    request_count += 1

    data = request.json
    amount = data.get('amount', 0)
    currency = data.get('currency', 'USD')

    # Simulate slow response
    if random.random() < SLOW_RESPONSE_RATE:
        time.sleep(SLOW_RESPONSE_DELAY)

    # Simulate random failures
    if random.random() < FAILURE_RATE:
        failure_count += 1
        return jsonify({
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500

    return jsonify({
        "transaction_id": f"txn_{request_count}",
        "amount": amount,
        "currency": currency,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/shipment', methods=['POST'])
def shipment():
    """Shipping endpoint with random failures"""
    global request_count, failure_count
    request_count += 1

    data = request.json
    address = data.get('address', '')

    # Simulate slow response
    if random.random() < SLOW_RESPONSE_RATE:
        time.sleep(SLOW_RESPONSE_DELAY)

    # Simulate random failures
    if random.random() < FAILURE_RATE:
        failure_count += 1
        return jsonify({
            "error": "Shipping service temporarily unavailable",
            "timestamp": datetime.now().isoformat()
        }), 503

    return jsonify({
        "shipment_id": f"ship_{request_count}",
        "address": address,
        "estimated_delivery": "2-3 business days",
        "status": "created",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/email', methods=['POST'])
def email():
    """Email endpoint with random failures"""
    global request_count, failure_count
    request_count += 1

    data = request.json
    recipient = data.get('to', '')
    subject = data.get('subject', '')

    # Simulate slow response
    if random.random() < SLOW_RESPONSE_RATE:
        time.sleep(SLOW_RESPONSE_DELAY)

    # Simulate random failures
    if random.random() < FAILURE_RATE:
        failure_count += 1
        return jsonify({
            "error": "Email service unavailable",
            "timestamp": datetime.now().isoformat()
        }), 500

    return jsonify({
        "message_id": f"msg_{request_count}",
        "to": recipient,
        "subject": subject,
        "status": "sent",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "total_requests": request_count,
        "failures": failure_count,
        "failure_rate": f"{(failure_count / request_count * 100) if request_count > 0 else 0:.1f}%"
    }), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    """Get API metrics"""
    return jsonify({
        "total_requests": request_count,
        "failures": failure_count,
        "success_rate": f"{((request_count - failure_count) / request_count * 100) if request_count > 0 else 0:.1f}%",
        "failure_rate": f"{(failure_count / request_count * 100) if request_count > 0 else 0:.1f}%"
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("MOCK API SERVER")
    print("=" * 60)
    print(f"Failure rate: {FAILURE_RATE * 100}%")
    print(f"Slow response rate: {SLOW_RESPONSE_RATE * 100}%")
    print(f"Slow response delay: {SLOW_RESPONSE_DELAY}s")
    print("\nEndpoints:")
    print("  POST /charge     - Process payment")
    print("  POST /shipment   - Create shipment")
    print("  POST /email      - Send email")
    print("  GET  /health     - Health check")
    print("  GET  /metrics    - API metrics")
    print("\nServer running on http://localhost:8080")
    print("=" * 60)

    app.run(host='0.0.0.0', port=8080, debug=False)
