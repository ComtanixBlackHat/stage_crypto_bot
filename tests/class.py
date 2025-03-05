import requests
import time
import hashlib
import hmac
import base64

class KrakenAPI:
    BASE_URL = "https://api.kraken.com"

    @staticmethod
    def get_current_price(pair: str):
        """Get the latest price for a trading pair."""
        url = f"{KrakenAPI.BASE_URL}/0/public/Ticker"
        response = requests.get(url, params={"pair": pair})
        data = response.json()
        # print("currentPrice response ", data)  # Debugging print

        if "error" in data and data["error"]:
            print("Kraken API Error:", data["error"])
            return None

        # Extract the correct key dynamically
        result = data.get("result", {})
        if not result:
            return None

        pair_key = list(result.keys())[0]  # Get the correct pair name returned by Kraken
        return result.get(pair_key, {}).get("c", [None])[0]

    @staticmethod
    def get_bid_ask(pair: str):
        """Get bid and ask prices for a trading pair."""
        url = f"{KrakenAPI.BASE_URL}/0/public/Ticker"
        response = requests.get(url, params={"pair": pair})
        data = response.json()
        result = data.get("result", {}).get(pair, {})
        bid = result.get("b", [None])[0]
        ask = result.get("a", [None])[0]
        return bid, ask

    @staticmethod
    def send_order(api_key: str, api_secret: str, pair: str, side: str, volume: float, price: float = None, order_type="market"):
        """Send a buy or sell order."""
        url = f"{KrakenAPI.BASE_URL}/0/private/AddOrder"
        nonce = str(int(time.time() * 1000))
        data = {
            "nonce": nonce,
            "ordertype": order_type,
            "type": side,
            "volume": str(volume),
            "pair": pair,
        }
        if price:
            data["price"] = str(price)

        headers = KrakenAPI._get_headers(url, data, api_key, api_secret)
        response = requests.post(url, headers=headers, data=data)
        return response.json()

    @staticmethod
    def _get_headers(url: str, data: dict, api_key: str, api_secret: str):
        """Generate authentication headers for private API requests."""
        post_data = "&".join([f"{key}={value}" for key, value in data.items()])
        encoded = (data["nonce"] + post_data).encode()
        message = url.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
        return {
            "API-Key": api_key,
            "API-Sign": base64.b64encode(signature.digest()).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

# Example usage
if __name__ == "__main__":
    pair = "BTCUSDT"
    print("Current Price:", KrakenAPI.get_current_price(pair))
    # print("Bid/Ask:", KrakenAPI.get_bid_ask(pair))

    # Send an order (Replace with valid API keys)
    # api_key = "your_api_key"
    # api_secret = "your_api_secret"
    # response = KrakenAPI.send_order(api_key, api_secret, "XXBTZUSD", "buy", 0.01)
    # print(response)
