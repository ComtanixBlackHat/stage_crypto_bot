import json
import asyncio
import websockets

class BinanceOHLCClient:
    def __init__(self, serverWS , symbols, interval=1):
        """Initialize BinanceOHLCClient with symbols to subscribe to and interval"""
        self.symbols = symbols
        self.interval = interval
        self.url = "wss://stream.binance.com:9443/stream"
        self.endStream = False
        self.serverWS = serverWS
    async def setEndStream(self, endStream):
        self.endStream = endStream

    async def on_message(self, message):
        """Handle incoming messages from the WebSocket server"""
        message = json.loads(message)
        data = message.get("data")
        if data:
            stream_data = data.get("k")
            if stream_data:
                symbol = stream_data.get("s")
                close = stream_data.get("c")
                print(f"Symbol: {symbol}, Close: {close}")
                await self.serverWS.send(json.dumps({
                    "s": symbol,
                    "c": float(close),
                }))
        else:
            print("Data is None", message)

    async def send_message(self, message):
        """Send message to the WebSocket"""
        # Example of sending a message back
        print(f"Sending message: {message}")
        # This could be modified to send messages to a different WebSocket or another service

    async def on_error(self, error):
        """Handle errors"""
        print(f"Error: {error}")

    async def on_open(self, websocket):
        """Send subscribe message when WebSocket opens"""
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [
                f"{symbol.lower()}@kline_{self.interval}m" for symbol in self.symbols
            ],
            "id": 1
        }
        await websocket.send(json.dumps(subscribe_message))

    async def subSymbol(self, symbol, interval):
        """Send subscribe message for a single symbol"""
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [
                f"{symbol.lower()}@kline_{interval}m"
            ],
            "id": 1
        }
        await self.ws.send(json.dumps(subscribe_message))

    async def run(self):
        """Start the WebSocket connection"""
        async with websockets.connect(self.url) as websocket:
            self.ws = websocket

            # Send subscribe message
            await self.on_open(websocket)

            # Start listening for messages
            while True:
                try:
                    message = await websocket.recv()
                    await self.on_message(message)
                except websockets.ConnectionClosed:
                    print("Connection closed")
                    break

    def start(self):
        """Start the WebSocket client asynchronously"""
        asyncio.run(self.run())

# Example usage
if __name__ == "__main__":
    symbols = ["BTCUSDT", "ETHUSDT"]  # Binance pairs
    binance_client = BinanceOHLCClient(symbols=symbols, interval=5)

    # Running WebSocket in an asynchronous event loop
    binance_client.start()
