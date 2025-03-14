from flask import Blueprint, request, jsonify
from app import db
from app.models import TradingPair
from app.controllers.crud.tradingpair import TradingPairCrud
from app.controllers.redisutil import RedisUtility
trading_pair_routes = Blueprint('trading_pair_routes', __name__)

# Create - Add a new trading pair
@trading_pair_routes.route('/', methods=['POST'])
def create_trading_pair():

    # Get JSON data from request
    data = request.get_json()
    print(data)
    # Validate data
    required_fields = ['symbol', 'initial_capital', 'take_profit_percentage', 
                       'rebuy_percentage', 'trade_usage_percentage']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Create a new trading pair
    try:

        TradingPairCrud.create_trading_pair(name= data['symbol'],
                                             initial_capital=data['initial_capital'] , 
                                             current_capital=data['initial_capital'] , 
                                             current_stage= 0, 
                                             take_profit_percentage=data['take_profit_percentage'] , 
                                             rebuy_percentage= data['rebuy_percentage'], 
                                             trade_usage_percentage= data['trade_usage_percentage']
                                                )
        

        return jsonify({"success": True}), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trading_pair_routes.route('/', methods=['GET'])
def get_trading_pairs():
    trading_pairs = TradingPair.query.all()

    # Serialize data into a list of dictionaries
    trading_pairs_list = [
        {
            "id": pair.id,
            "name": pair.name,
            "initial_capital": pair.initial_capital,
            "current_capital": pair.current_capital,
            "start_capital": pair.start_capital,
            "currentStage": pair.currentStage,
            "take_profit_percentage": pair.take_profit_percentage,
            "rebuy_percentage": pair.rebuy_percentage,
            "trade_usage_percentage": pair.trade_usage_percentage,
            "status": pair.status,
            "start_date": pair.start_date.strftime("%Y-%m-%d %H:%M:%S"),  # Format date
            "user_id": pair.user_id ,
            "profit" : TradingPairCrud.get_pln_sum(pair.id),
            # "ispause" : "0" 
            "ispause": RedisUtility.get_hash_field(
                "symbol", RedisUtility.get_key(pair.name + "StreamSymbol")
            ) or "0"  # Default to "0" if None
            # RedisUtility.set_hash_field("symbol" , name , "1")
        }
        for pair in trading_pairs
    ]
#  
    return jsonify(trading_pairs_list)


@trading_pair_routes.route('/<int:id>', methods=['GET'])
def get_trading_pair(id):
    pair = TradingPair.query.get(id)
    print(pair)
    if pair:
        return jsonify({
            "id": pair.id,
            "name": pair.name,
            "initial_capital": pair.initial_capital,
            "current_capital": pair.current_capital,
            "currentStage": pair.currentStage,
            "take_profit_percentage": pair.take_profit_percentage,
            "rebuy_percentage": pair.rebuy_percentage,
            "trade_usage_percentage": pair.trade_usage_percentage,
            "status": pair.status,
            "start_date": pair.start_date.strftime("%Y-%m-%d %H:%M:%S"),  # Format date
            "user_id": pair.user_id
        })
    else:
        return jsonify({'error': 'Trading pair not found'}), 404

# Update - Update a trading pair by ID
@trading_pair_routes.route('/<int:id>', methods=['PUT'])
def update_trading_pair(id):
    data = request.get_json()
    success = False
    capital = data.get('current_capital')
    takeProfit = data.get("takeProfit")
    rebuy = data.get("rebuy")
    tradeUsage =data.get("tradeUsage") 
    try:
        
        if capital is not None: 
            success = TradingPairCrud.update_trading_pair_capital(id, capital)
            
        
        if takeProfit is not None:
            success = TradingPairCrud.update_trading_pair_TakeProfit(id, takeProfit)
        
        if rebuy is not None:
            success = TradingPairCrud.update_trading_pair_ReBuy(id, rebuy)
        
        if tradeUsage is not None:
            success = TradingPairCrud.update_trading_pair_tradeUsage(id, tradeUsage)
        
        if success:
            return jsonify({'message': 'Trading pair updated successfully'}), 200
        else:
            return jsonify({'error': 'Trading pair not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



@trading_pair_routes.route('/<int:id>/pause', methods=['PUT'])
def update_pause_trading_pair(id):
    try:
        pair = TradingPair.query.get(id)
        
        if not pair:
            return jsonify({'error': 'Trading pair not found'}), 404
        
        streamSymbol = RedisUtility.get_key(pair.name+"StreamSymbol")
        
        current_status = RedisUtility.get_hash_field("symbol", streamSymbol)
        if current_status == "1":
            RedisUtility.set_hash_field("symbol", streamSymbol, "0")
            return jsonify({'message': 'Trading pair paused'}), 200
        elif current_status == "0":
            RedisUtility.set_hash_field("symbol", streamSymbol, "1")
            return jsonify({'message': 'Trading pair resumed'}), 200
        else:
            return jsonify({'error': 'Invalid trading pair status'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400



# Delete - Delete a trading pair by ID
@trading_pair_routes.route('/<int:id>', methods=['DELETE'])
def delete_trading_pair(id):
    """
    API endpoint to delete a trading pair by ID.
    """
    success = TradingPairCrud.delete_trading_pair(id)
    
    if success:
        return jsonify({'message': 'Trading pair deleted successfully'}), 200
    else:
        return jsonify({'error': 'Trading pair not found'}), 404


