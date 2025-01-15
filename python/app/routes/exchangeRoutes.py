from flask import Blueprint, jsonify
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
