from flask import Blueprint, request, jsonify
from app import db
from app.models.transaction import Transaction

transaction_routes = Blueprint('transaction_routes', __name__)

@transaction_routes.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([{
        'id': transaction.id,
        'type': transaction.type,
        'amount': transaction.amount,
        'price': transaction.price
    } for transaction in transactions])

@transaction_routes.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    new_transaction = Transaction(
        position_id=data['position_id'],
        amount=data['amount'],
        price=data['price'],
        type=data['type']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction created successfully'}), 201
