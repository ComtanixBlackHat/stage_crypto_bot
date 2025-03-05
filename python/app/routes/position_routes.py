from flask import Blueprint, request, jsonify
from app import db
from app.models import Position
from app.controllers.crud.positionCrud import PositionCRUD , OldPosition
from app.controllers.redisutil import RedisUtility
from app.exchanges.kerkaren.kraken import Kraken
position_routes = Blueprint('position_routes', __name__)

# Create - Add a new position
# route = localhost:5000/api/positions
@position_routes.route('/', methods=['POST'])
def create_position():
    data = request.get_json()
    try:
        currentPrice = data['curentPrice']

        symbol = data['symbol']
        currentStageKey = symbol+"currentStage"
        
        currentStage = RedisUtility.get_key(currentStageKey)
        take_profit_percentage = float(RedisUtility.get_key(symbol+"take_profit_percentage"))
        rebuy_percentage = float(RedisUtility.get_key(symbol+"take_profit_percentage"))
        current_capital = float(RedisUtility.get_key(symbol+"current_capital"))
        trade_usage_percentage = float(RedisUtility.get_key(symbol+"trade_usage_percentage"))
        
        
        take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
        rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
        priceInUsdt = current_capital * (trade_usage_percentage / 100)
        ammount = priceInUsdt/currentPrice



        currentPrice = Kraken.get_current_price(symbol)
        currentPrice = 0
        PositionCRUD.create_position(
            int(currentStage), 1, data['symbol'] , rebuy_price , currentPrice ,
              ammount , "Open" , take_profit_price , "0.0" , data.get('raw_response', {}) 
        )

        return jsonify({'message': 'Position created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400



position_routes = Blueprint('position_routes', __name__)

# Read - Get filtered positions
@position_routes.route('/', methods=['GET'])
def get_positions():
    status_param = request.args.get('status', default='Open,Waiting', type=str)
    symbol_param = request.args.get('symbol', type=int)  # Keep as string to allow flexible input
    print(symbol_param)
    # Convert status to a list if comma-separated
    status_list = [s.strip() for s in status_param.split(',')]

    # Build the query
    query = db.session.query(Position).filter(Position.status.in_(status_list))

    # If symbol is provided, filter by it
    if symbol_param:
        query = query.filter(Position.trading_pair_id == symbol_param)

    positions = query.all()

    # Prepare the response
    positions_list = [{
        'id': position.id,
        'stage': position.stage,
        'trading_pair_id': position.trading_pair_id,
        'buy_price': position.buy_price,
        'current_buy_price': position.current_buy_price,
        'sell_price': position.sell_price,
        'amount': position.amount,
        'pln': position.pln,
        'raw_response': position.raw_response,
        'created_at': position.created_at,
        'status': position.status
    } for position in positions]

    return jsonify(positions_list)


@position_routes.route('/closed', methods=['GET'])
def get_positionsu():
    symbol_param = request.args.get('symbol', type=int)  # Expect an integer
    print(symbol_param)

    query = OldPosition.query  # Define query before filtering

    if symbol_param:
        query = query.filter(OldPosition.trading_pair_id == symbol_param)

    positions = query.all()

    # Prepare the response
    positions_list = [{
        'id': position.id,
        'stage': position.stage,
        'trading_pair_id': position.trading_pair_id,
        'buy_price': position.buy_price,
        'current_buy_price': position.current_buy_price,
        'sell_price': position.sell_price,
        'amount': position.amount,
        'pln': position.pln,
        'raw_response': position.raw_response,
        'start_at': position.start_at.isoformat(),
        'end_at': position.end_at.isoformat(),  # Ensure datetime serialization
        'status': position.status
    } for position in positions]

    return jsonify(positions_list)

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