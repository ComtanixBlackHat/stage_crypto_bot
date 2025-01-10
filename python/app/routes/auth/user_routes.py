from flask import Blueprint, request, jsonify
from app import db
from app.models import Transaction

transaction_routes = Blueprint('transaction_routes', __name__)

# Create - Add a new transaction
@transaction_routes.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    try:
        new_transaction = Transaction(
            position_id=data['position_id'],
            amount=data['amount'],
            price=data['price'],
            type=data['type'],
            timestamp=data.get('timestamp', datetime.utcnow())
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Read - Get all transactions
@transaction_routes.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([{
        'id': transaction.id,
        'position_id': transaction.position_id,
        'amount': transaction.amount,
        'price': transaction.price,
        'type': transaction.type,
        'timestamp': transaction.timestamp
    } for transaction in transactions])

# Read - Get a single transaction by ID
@transaction_routes.route('/transaction/<int:id>', methods=['GET'])
def get_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        return jsonify({
            'id': transaction.id,
            'position_id': transaction.position_id,
            'amount': transaction.amount,
            'price': transaction.price,
            'type': transaction.type,
            'timestamp': transaction.timestamp
        })
    else:
        return jsonify({'error': 'Transaction not found'}), 404

# Update - Update a transaction by ID
@transaction_routes.route('/transaction/<int:id>', methods=['PUT'])
def update_transaction(id):
    data = request.get_json()
    transaction = Transaction.query.get(id)
    if transaction:
        try:
            transaction.amount = data.get('amount', transaction.amount)
            transaction.price = data.get('price', transaction.price)
            transaction.type = data.get('type', transaction.type)
            transaction.timestamp = data.get('timestamp', transaction.timestamp)
            
            db.session.commit()
            return jsonify({'message': 'Transaction updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Transaction not found'}), 404

# Delete - Delete a transaction by ID
@transaction_routes.route('/transaction/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        try:
            db.session.delete(transaction)
            db.session.commit()
            return jsonify({'message': 'Transaction deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Transaction not found'}), 404
