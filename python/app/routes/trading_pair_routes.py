from flask import Blueprint, request, jsonify
from app import db
from app.models import TradingPair

trading_pair_routes = Blueprint('trading_pair_routes', __name__)

# Create - Add a new trading pair
@trading_pair_routes.route('/trading_pair', methods=['POST'])
def create_trading_pair():
    data = request.get_json()
    try:
        new_pair = TradingPair(
            name=data['name'],
            initial_capital=data['initial_capital'],
            current_capital=data['current_capital'],
            rebuy_price=data['rebuy_price'],
            take_profit_percentage=data['take_profit_percentage'],
            rebuy_percentage=data['rebuy_percentage'],
            trade_usage_percentage=data['trade_usage_percentage'],
            user_id=data['user_id']
        )
        db.session.add(new_pair)
        db.session.commit()
        return jsonify({'message': 'Trading pair created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Read - Get all trading pairs
@trading_pair_routes.route('/trading_pairs', methods=['GET'])
def get_trading_pairs():
    trading_pairs = TradingPair.query.all()
    return jsonify([{
        'id': pair.id,
        'name': pair.name,
        'initial_capital': pair.initial_capital,
        'current_capital': pair.current_capital,
        'status': pair.status,
        'start_date': pair.start_date
    } for pair in trading_pairs])

# Read - Get a single trading pair by ID
@trading_pair_routes.route('/trading_pair/<int:id>', methods=['GET'])
def get_trading_pair(id):
    pair = TradingPair.query.get(id)
    if pair:
        return jsonify({
            'id': pair.id,
            'name': pair.name,
            'initial_capital': pair.initial_capital,
            'current_capital': pair.current_capital,
            'rebuy_price': pair.rebuy_price,
            'take_profit_percentage': pair.take_profit_percentage,
            'rebuy_percentage': pair.rebuy_percentage,
            'trade_usage_percentage': pair.trade_usage_percentage,
            'status': pair.status,
            'start_date': pair.start_date,
            'user_id': pair.user_id
        })
    else:
        return jsonify({'error': 'Trading pair not found'}), 404

# Update - Update a trading pair by ID
@trading_pair_routes.route('/trading_pair/<int:id>', methods=['PUT'])
def update_trading_pair(id):
    data = request.get_json()
    pair = TradingPair.query.get(id)
    if pair:
        try:
            pair.name = data.get('name', pair.name)
            pair.initial_capital = data.get('initial_capital', pair.initial_capital)
            pair.current_capital = data.get('current_capital', pair.current_capital)
            pair.rebuy_price = data.get('rebuy_price', pair.rebuy_price)
            pair.take_profit_percentage = data.get('take_profit_percentage', pair.take_profit_percentage)
            pair.rebuy_percentage = data.get('rebuy_percentage', pair.rebuy_percentage)
            pair.trade_usage_percentage = data.get('trade_usage_percentage', pair.trade_usage_percentage)
            pair.status = data.get('status', pair.status)
            
            db.session.commit()
            return jsonify({'message': 'Trading pair updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Trading pair not found'}), 404

# Delete - Delete a trading pair by ID
@trading_pair_routes.route('/trading_pair/<int:id>', methods=['DELETE'])
def delete_trading_pair(id):
    pair = TradingPair.query.get(id)
    if pair:
        try:
            db.session.delete(pair)
            db.session.commit()
            return jsonify({'message': 'Trading pair deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Trading pair not found'}), 404


