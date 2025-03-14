import requests
import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode
import json
# api_key = "Sc1rIvjDK4LaNzmQ7IfcrjlfLtRP7l2DyXuQK62gM6vTTghHQgcaL2PZ"
# api_secret = "wsQzohrIl6SUX0sUa10uWO7iPQ+T5mc4q4YjubYXOq1jgyWnZum1Wj8nncj/WajsVXt9SUj9iBOhhduJ5Vf/jw=="
# API_URL = "https://api.kraken.com"
api_key = "Sc1rIvjDK4LaNzmQ7IfcrjlfLtRP7l2DyXuQK62gM6vTTghHQgcaL2PZ"
api_secret = "wsQzohrIl6SUX0sUa10uWO7iPQ+T5mc4q4YjubYXOq1jgyWnZum1Wj8nncj/WajsVXt9SUj9iBOhhduJ5Vf/jw=="
API_URL = "https://api.kraken.com"
class Kraken:

    @staticmethod
    def _get_signature(url_path, data, api_secret, nonce):
        """
        Generate a Kraken API signature.
        """
        postdata = data.encode()
        message = url_path.encode() + hashlib.sha256(nonce.encode() + postdata).digest()
        mac = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
        return base64.b64encode(mac.digest()).decode()

    @staticmethod
    def query_orders(txid, trades=False, userref=None, consolidate_taker=True):
        # API URL
        # url = "https://api.kraken.com/0/private/QueryOrders"
        
        # Prepare the data to send in the request
        payload = {
            'nonce': str(int(time.time() * 1000)),  # Generate a nonce for the request
            'txid': txid,
            'trades': trades,
            
            'consolidate_taker': consolidate_taker
        }
        url_path =  "/0/private/QueryOrders"
        url = API_URL + url_path
        nonce = str(int(time.time() * 1000))
        # Generate the signature
        signature = Kraken._get_signature(url_path, urlencode(payload), api_secret, nonce)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'API-Key': api_key,
            'API-Sign': signature
        }      
        # Call the Kraken API here using your preferred HTTP library (requests, etc.)
        response = requests.post(url, data=payload, headers=headers)
        print(response.json())
        return response.json()  # Assuming the response is JSON formatted

    @staticmethod
    def send_order(pair, type, volume, ordertype="market", price=None, cl_ord_id=None):
        """
        Send an order to Kraken API.

        :param pair: Asset pair (e.g., 'XBTUSD').
        :param type: Order type ('buy' or 'sell').
        :param ordertype: Order execution type (e.g., 'market', 'limit').
        :param volume: Volume of the order.
        :param price: Price (required for limit orders).
        :param cl_ord_id: Optional client order ID for the order.
        :return: Response from the Kraken API.
        """
        url_path = "/0/private/AddOrder"
        url = API_URL + url_path
        nonce = str(int(time.time() * 1000))

        # Prepare payload
        payload = {
            "nonce": nonce,
            "ordertype": ordertype,
            "type": type,
            "volume": volume,
            "pair": pair,
        }
        
        if cl_ord_id:
            payload["cl_ord_id"] = cl_ord_id
        if ordertype == "limit" and price:
            payload["price"] = price

        print(payload)
        # Generate the signature
        signature = Kraken._get_signature(url_path, urlencode(payload), api_secret, nonce)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'API-Key': api_key,
            'API-Sign': signature
        }

        # Send the request
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def get_symbols():
        """
        Retrieve all tradable symbols from Kraken.

        :return: List of tradable symbols or an error message.
        """
        url = "https://api.kraken.com/0/public/AssetPairs"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["error"]:
                return {"error": "Failed to retrieve symbols"}
            # s
            # symbols = list(data["result"].keys())
            symbols = [
                        "BTC/USD" , "ETH/USD" , "XRP/USD" , "SOL/USD"  
                       , "LTC/USD" , "ADA/USD" , "DODGE/USD" , "TRUMP/USD" , "LINK/USD",
                         "AAVE/USD" , "PEPE/USD" , "ALGO/USD" , "XLM/USD" , "DOT/USD" , 
                         "AVAX/USD" , "TRX/USD"  , "XMR/USD" , "APT/USD",
                         "CRV/USD" , "UNI/USD" , "ICP/USD" , "SHIB/USD"  , "ATOM/USD" , 
                         "FIL/USD" , "AKT/USD" , "POL/USD" , "MANA/USD", "BCH/USD", "SAND/USD",
                         "ETC/USD", "EOS/USD" , "CHZ/USD", "GALA/USD", "LUNA/USD", "ETH/BTC"
                         ]
            return {"symbols": symbols}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


    @staticmethod
    def get_current_price(pair: str):
        """Get the latest price for a trading pair."""
        url = f"{API_URL}/0/public/Ticker"
        response = requests.get(url, params={"pair": pair})
        data = response.json()
        print("currentPrice response ", data)  # Debugging print

        if "error" in data and data["error"]:
            print("Kraken API Error:", data["error"])
            return None

        # Extract the correct key dynamically
        result = data.get("result", {})
        if not result:
            return None

        # Get the first key (trading pair) dynamically
        pair_key = next(iter(result), None)
        if not pair_key:
            return None

        # Extract the latest trade price (close price)
        return float(result[pair_key]["c"][0])

    @staticmethod
    def orderFillChecker(data):
        for _ in range(10):  # Run the loop 10 times
            txid = data["result"]["txid"][0]  # Get the first transaction ID
            print(txid)

            trades = data.get('trades', False)
            userref = data.get('userref', None)
            consolidate_taker = data.get('consolidate_taker', True)

            orderDetail = Kraken.query_orders(txid, trades, userref, consolidate_taker)
            print(orderDetail)

            if orderDetail["result"]:
                print("*************************************")
                if orderDetail["result"][txid]["status"] == "closed":
                    print(orderDetail["result"])
                    return orderDetail

            time.sleep(3)  # Wait before the next check

        print("Order not filled within 10 attempts.")
        return None  # Return None if the order is not filled after 10 tries


# curl -X POST http://127.0.0.1:5000/bot/stage-complete      -H "Content-Type: application/json"      -d '{
# "symbol": "AAVEUSD",
# "hitType": "TakeProfit"
# }'