import requests
import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode

api_key = "K8XjH+NigeGRIhPe7TKeDTXkOJnEzDQhC7xFkfZgQ5A2ItiweuXgzXXf"
api_secret = "rgjj1yFtk5qgOwZu7OJ7x5AmajhHpCIE+BOekKTzakZ+FbIz9CmfTGA7UeNAgtZU27AEKYb2jbH7lt0UPkH3O1QF"

class Kraken:
    API_URL = "https://demo-api.kraken.com"
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
    def send_order(pair, type, ordertype, volume, price=None):
        """
        Send an order to Kraken API.

        :param api_key: Kraken API key.
        :param api_secret: Kraken API secret.
        :param pair: Asset pair (e.g., 'XBTUSD').
        :param type: Order type ('buy' or 'sell').
        :param ordertype: Order execution type (e.g., 'market', 'limit').
        :param volume: Volume of the order.
        :param price: Price (required for limit orders).
        :return: Response from the Kraken API.
        """
        url_path = "/0/private/AddOrder"
        url = Kraken.API_URL + url_path
        nonce = str(int(time.time() * 1000))

        # Prepare payload
        payload = {
            "nonce": nonce,
            "pair": pair,
            "type": type,
            "ordertype": ordertype,
            "volume": volume,
        }
        if ordertype == "limit" and price is not None:
            payload["price"] = price

        # Add headers
        headers = {
            "API-Key": api_key,
            "API-Sign": Kraken._get_signature(url_path, urlencode(payload), api_secret, nonce),
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
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

            symbols = list(data["result"].keys())
            return {"symbols": symbols}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


    @staticmethod
    def get_current_kraken_chart(pair="XBTUSD", interval=60):
        """
        Fetches the most recent OHLC data from Kraken.
        
        Args:
            pair (str): The trading pair to fetch data for (e.g., "XBTUSD", "ETHUSD").
            interval (int): Timeframe in minutes (e.g., 1, 5, 15, 60, 240, etc.).

        Returns:
            list: A list of OHLC data where each entry contains:
                [timestamp, open, high, low, close, vwap, volume, count]
                - timestamp: UNIX time of the start of the interval
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - vwap: Volume-weighted average price
                - volume: Total volume traded during the interval
                - count: Number of trades during the interval
            None: If an error occurs or no data is available.
        """
        # Kraken API endpoint for OHLC data
        url = "https://api.kraken.com/0/public/OHLC"
        params = {
            "pair": pair,
            "interval": interval
        }

        try:
            # Make the request
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            print(data)
            # Handle API errors
            if data.get("error"):
                print("Error from Kraken API:", data["error"])
                return None

            # Extract OHLC data
            key = f"X{pair.replace('/', '')}"
            ohlc_data = data["result"].get(key, [])

            if not ohlc_data:
                print(f"No data found for pair {pair}.")
                return None

            return ohlc_data

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching data: {e}")
            return None
