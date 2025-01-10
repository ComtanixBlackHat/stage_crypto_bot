from flask import Blueprint, request, jsonify
from app import db
from app.models import Position

position_routes = Blueprint('position_routes', __name__)

# Create - Add a new position
@position_routes.route('/position', methods=['POST'])
def create_position():
    data = request.get_json()
    try:
        new_position = Position(
            stage=data['stage'],
            trading_pair_id=data['trading_pair_id'],
            buy_price=data['buy_price'],
            amount=data['amount'],
            sell_price=data.get('sell_price', None),
            pln=data.get('pln', None),
            raw_response=data.get('raw_response', None),
            status=data.get('status', "Open")
        )
        db.session.add(new_position)
        db.session.commit()
        return jsonify({'message': 'Position created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Read - Get all positions
@position_routes.route('/positions', methods=['GET'])
def get_positions():
    positions = Position.query.all()
    return jsonify([{
        'id': position.id,
        'stage': position.stage,
        'trading_pair_id': position.trading_pair_id,
        'buy_price': position.buy_price,
        'sell_price': position.sell_price,
        'amount': position.amount,
        'pln': position.pln,
        'status': position.status,
        'created_at': position.created_at
    } for position in positions])

# Read - Get a single position by ID
@position_routes.route('/position/<int:id>', methods=['GET'])
def get_position(id):
    position = Position.query.get(id)
    if position:
        return jsonify({
            'id': position.id,
            'stage': position.stage,
            'trading_pair_id': position.trading_pair_id,
            'buy_price': position.buy_price,
            'sell_price': position.sell_price,
            'amount': position.amount,
            'pln': position.pln,
            'status': position.status,
            'created_at': position.created_at
        })
    else:
        return jsonify({'error': 'Position not found'}), 404

# Update - Update a position by ID
@position_routes.route('/position/<int:id>', methods=['PUT'])
def update_position(id):
    data = request.get_json()
    position = Position.query.get(id)
    if position:
        try:
            position.stage = data.get('stage', position.stage)
            position.buy_price = data.get('buy_price', position.buy_price)
            position.sell_price = data.get('sell_price', position.sell_price)
            position.amount = data.get('amount', position.amount)
            position.pln = data.get('pln', position.pln)
            position.raw_response = data.get('raw_response', position.raw_response)
            position.status = data.get('status', position.status)
            
            db.session.commit()
            return jsonify({'message': 'Position updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Position not found'}), 404

# Delete - Delete a position by ID
@position_routes.route('/position/<int:id>', methods=['DELETE'])
def delete_position(id):
    position = Position.query.get(id)
    if position:
        try:
            db.session.delete(position)
            db.session.commit()
            return jsonify({'message': 'Position deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Position not found'}), 404
