from flask import Blueprint, request, jsonify
from app.exchanges.kerkaren.kraken import Kraken
import requests
kraken_routes = Blueprint('kraken_routes', __name__)

@kraken_routes.route('/symbols/<exchanges>', methods=['GET'])
def get_symbols(exchanges):
    # Check if the exchange is Kraken (or any other exchange)
    if exchanges.lower() == 'kraken':
        result = Kraken.get_symbols()  # Call the static method get_symbols from Kraken class
        print("data")
    else:
        result = {'error': 'Unsupported exchange'}
    
    # Return the result as a JSON response
    return jsonify(result), 200

@kraken_routes.route('/query_orders/<exchanges>', methods=['POST'])
def query_orders_route(exchanges):
    try:
        # Get data from the request JSON payload
        data = request.get_json()

        # Extract parameters from the request data
        txid = data.get('txid')  # Kraken order identifier(s)
        trades = data.get('trades', False)  # Whether or not to include trades related to the position
        userref = data.get('userref', None)  # Optional user reference ID
        consolidate_taker = data.get('consolidate_taker', True)  # Whether or not to consolidate taker trades

        if not txid:
            return jsonify({"error": "Missing txid parameter"}), 400

        # Call the query_orders method from the Kraken class
        if exchanges.lower() == 'kraken':
            response = Kraken.query_orders(txid, trades, userref, consolidate_taker)
            print(response)
        else:
            response = {'error': 'Unsupported exchange'}
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@kraken_routes.route('/send_order/<exchanges>', methods=['POST'])
def send_order_route(exchanges):
    try:
        print("i")
        # Get data from the request JSON payload
        data = request.get_json()

        # Extract parameters from the request data
        pair = data.get('pair')
        type = data.get('type')
        order_subtype = data.get('ordertype')  # For example: 'market' or 'limit'
        volume = data.get('volume')
        price = data.get('price', None)  # price is optional for limit orders

        if not all([pair, type, order_subtype, volume]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the send_order method from the Kraken class
        
        if exchanges.lower() == 'kraken':
            pair = "SOLUSD"
            volume="0.1"
            response = Kraken.send_order(pair , type , volume)
            # response = Kraken.send_order(pair, order_type, order_subtype, volume, price)  # Call the static method get_symbols from Kraken class
            print(response)
        else:
            response = {'error': 'Unsupported exchange'}
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kraken_routes.route('/OHLC/<exchange>', methods=['POST'])
def get_chart(exchange):
    """
    API endpoint to fetch OHLC data from Kraken.
    Query parameters:
        pair (str): The trading pair (default: "XBTUSD").
        interval (int): Timeframe in minutes (default: 60).

    Returns:
        JSON: OHLC data or an error message.
    """
    pair = request.args.get('pair', 'XBTUSD')
    interval = request.args.get('interval', 60)

    try:
        # Ensure interval is an integer
        interval = int(interval)
    except ValueError:
        return jsonify({"error": "Invalid interval, must be an integer."}), 400

    if exchange.lower() == 'kraken':
        # Fetch data from Kraken
        response = Kraken.get_current_kraken_chart(pair, interval)  # Call the appropriate method from Kraken class
        # if "error" in response:
        #     return jsonify(response), 400
        return jsonify({
            "exchange": exchange,
            "pair": pair,
            "interval": interval,
            "ohlc_data": response
        })
    else:
        # Unsupported exchange
        return jsonify({"error": "Unsupported exchange"}), 400
