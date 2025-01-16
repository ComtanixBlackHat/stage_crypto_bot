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


@kraken_routes.route('/send_order/<exchanges>', methods=['POST'])
def send_order_route(exchanges):
    try:
        print("i")
        # Get data from the request JSON payload
        data = request.get_json()

        # Extract parameters from the request data
        pair = data.get('pair')
        order_type = data.get('type')
        order_subtype = data.get('ordertype')  # For example: 'market' or 'limit'
        volume = data.get('volume')
        price = data.get('price', None)  # price is optional for limit orders

        if not all([pair, order_type, order_subtype, volume]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the send_order method from the Kraken class
        
        if exchanges.lower() == 'kraken':
            response = Kraken.send_order(pair, order_type, order_subtype, volume, price)  # Call the static method get_symbols from Kraken class
            print(response)
        else:
            response = {'error': 'Unsupported exchange'}
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500