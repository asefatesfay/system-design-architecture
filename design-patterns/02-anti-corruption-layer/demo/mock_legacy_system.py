"""
Mock Legacy System API
Simulates an old legacy system with:
- Cryptic field names (F_NAME, CUST_ID, STATUS_CD)
- Weird date formats (YYYYMMDDHHMMSS)
- Status codes instead of readable values
- Flat data structures
"""

from flask import Flask, request, jsonify
from datetime import datetime
import random
import string

app = Flask(__name__)

# In-memory storage
customers = {}
orders = {}
next_customer_id = 1
next_order_id = 1


def generate_customer_id():
    """Generate legacy-style customer ID"""
    global next_customer_id
    cust_id = f"CUST{next_customer_id:06d}"
    next_customer_id += 1
    return cust_id


def generate_order_id():
    """Generate legacy-style order ID"""
    global next_order_id
    ord_id = f"ORD{next_order_id:08d}"
    next_order_id += 1
    return ord_id


@app.route('/customers', methods=['POST'])
def create_customer():
    """Create customer with legacy format"""
    data = request.json

    # Validate legacy format fields
    required_fields = ['F_NAME', 'L_NAME', 'EMAIL_ADDR', 'ADDR_LN1', 'ADDR_CITY', 'ADDR_ZIP']
    for field in required_fields:
        if field not in data:
            return jsonify({"ERROR_CD": "MISSING_FIELD", "ERROR_MSG": f"Missing {field}"}), 400

    customer_id = generate_customer_id()

    # Store with legacy format
    customer = {
        "CUST_ID": customer_id,
        "F_NAME": data['F_NAME'],
        "L_NAME": data['L_NAME'],
        "EMAIL_ADDR": data['EMAIL_ADDR'],
        "ADDR_LN1": data['ADDR_LN1'],
        "ADDR_CITY": data['ADDR_CITY'],
        "ADDR_ZIP": data['ADDR_ZIP'],
        "STATUS_CD": data.get('STATUS_CD', 'A'),  # Default to Active
        "CUST_TYP": data.get('CUST_TYP', 'R'),  # Default to Regular
        "CREATE_DT": data.get('CREATE_DT', datetime.now().strftime("%Y%m%d%H%M%S")),
        "UPDATE_DT": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    customers[customer_id] = customer

    return jsonify(customer), 201


@app.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer with legacy format"""
    if customer_id not in customers:
        return jsonify({
            "ERROR_CD": "NOT_FOUND",
            "ERROR_MSG": f"Customer {customer_id} not found"
        }), 404

    return jsonify(customers[customer_id]), 200


@app.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    if customer_id not in customers:
        return jsonify({"ERROR_CD": "NOT_FOUND"}), 404

    data = request.json
    customer = customers[customer_id]

    # Update fields
    if 'STATUS_CD' in data:
        customer['STATUS_CD'] = data['STATUS_CD']
    if 'CUST_TYP' in data:
        customer['CUST_TYP'] = data['CUST_TYP']
    if 'F_NAME' in data:
        customer['F_NAME'] = data['F_NAME']
    if 'L_NAME' in data:
        customer['L_NAME'] = data['L_NAME']

    customer['UPDATE_DT'] = datetime.now().strftime("%Y%m%d%H%M%S")

    return jsonify(customer), 200


@app.route('/customers', methods=['GET'])
def list_customers():
    """List all customers"""
    return jsonify(list(customers.values())), 200


@app.route('/orders', methods=['POST'])
def create_order():
    """Create order with legacy format"""
    data = request.json

    # Validate
    required_fields = ['CUST_ID', 'ORD_ITM_LST', 'SHIP_ADDR_LN1', 'SHIP_ADDR_CITY', 'SHIP_ADDR_ZIP']
    for field in required_fields:
        if field not in data:
            return jsonify({"ERROR_CD": "MISSING_FIELD", "ERROR_MSG": f"Missing {field}"}), 400

    # Check customer exists
    if data['CUST_ID'] not in customers:
        return jsonify({"ERROR_CD": "INVALID_CUST"}), 400

    order_id = generate_order_id()

    # Store with legacy format
    order = {
        "ORD_ID": order_id,
        "CUST_ID": data['CUST_ID'],
        "ORD_DT": data.get('ORD_DT', datetime.now().strftime("%Y%m%d")),
        "ORD_ITM_LST": data['ORD_ITM_LST'],
        "ORD_STATUS": data.get('ORD_STATUS', 'P'),  # Default to Pending
        "SHIP_ADDR_LN1": data['SHIP_ADDR_LN1'],
        "SHIP_ADDR_CITY": data['SHIP_ADDR_CITY'],
        "SHIP_ADDR_ZIP": data['SHIP_ADDR_ZIP'],
        "CREATE_DT": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    orders[order_id] = order

    return jsonify(order), 201


@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order with legacy format"""
    if order_id not in orders:
        return jsonify({"ERROR_CD": "NOT_FOUND"}), 404

    return jsonify(orders[order_id]), 200


@app.route('/orders', methods=['GET'])
def list_orders():
    """List orders (optionally filtered by customer)"""
    cust_id = request.args.get('cust_id')

    if cust_id:
        customer_orders = [o for o in orders.values() if o['CUST_ID'] == cust_id]
        return jsonify(customer_orders), 200

    return jsonify(list(orders.values())), 200


@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order status"""
    if order_id not in orders:
        return jsonify({"ERROR_CD": "NOT_FOUND"}), 404

    data = request.json
    order = orders[order_id]

    if 'ORD_STATUS' in data:
        order['ORD_STATUS'] = data['ORD_STATUS']

    order['UPDATE_DT'] = datetime.now().strftime("%Y%m%d%H%M%S")

    return jsonify(order), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "STATUS": "OK",
        "SYS_DT": datetime.now().strftime("%Y%m%d%H%M%S"),
        "CUST_CNT": len(customers),
        "ORD_CNT": len(orders)
    }), 200


@app.route('/reset', methods=['POST'])
def reset():
    """Reset all data (for testing)"""
    global customers, orders, next_customer_id, next_order_id
    customers = {}
    orders = {}
    next_customer_id = 1
    next_order_id = 1
    return jsonify({"STATUS": "RESET_OK"}), 200


if __name__ == '__main__':
    print("=" * 70)
    print(" " * 20 + "LEGACY SYSTEM API")
    print("=" * 70)
    print("\n🏛️  Simulating old legacy system with:")
    print("   • Cryptic field names (F_NAME, CUST_ID, STATUS_CD)")
    print("   • Weird date formats (YYYYMMDDHHMMSS)")
    print("   • Status codes (A=Active, I=Inactive, P=Pending)")
    print("   • Flat data structures (no nesting)")
    print("\nEndpoints:")
    print("   POST   /customers         - Create customer")
    print("   GET    /customers/:id     - Get customer")
    print("   PUT    /customers/:id     - Update customer")
    print("   GET    /customers         - List customers")
    print("   POST   /orders            - Create order")
    print("   GET    /orders/:id        - Get order")
    print("   GET    /orders?cust_id=X  - List customer orders")
    print("   PUT    /orders/:id        - Update order")
    print("   GET    /health            - Health check")
    print("   POST   /reset             - Reset data")
    print("\nServer running on http://localhost:8081")
    print("=" * 70)

    app.run(host='0.0.0.0', port=8081, debug=False)
