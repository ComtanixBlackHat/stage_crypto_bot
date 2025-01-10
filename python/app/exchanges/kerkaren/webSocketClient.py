import websocket
import json
import threading
import asyncio
import aiohttp
import websockets
class KrakenOHLCClient:
    def __init__(self, websocket , symbols, interval=1, snapshot=True ):
        """Initialize KrakenOHLCClient with symbols to subscribe to and interval"""
        self.symbols = symbols
        self.interval = interval
        self.snapshot = snapshot
        self.url = "wss://ws.kraken.com/v2"
        self.ws = None
        self.websocket = websocket
        self.endStream = False


    async def setEndStream(self , endStream):
        self.endStream = endStream

 
    async def runForever(self):
        while True:
            try:
                
                await self.websocket.ping()
                print("Connected")
               
                await self.stream()
                await asyncio.sleep(1) 
            except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError):
                print("Not Connected")
                break
                # create new connection

    def on_message(self, ws, message):
        """Handle incoming messages from the WebSocket server"""
        message = json.loads(message)
        data = message.get("data")
        if data is not None:
            self.websocket.send(json.dumps({
                    "s" : data.get("symbol"),
                    "c" : data.get("close") , 

            }))    
        else:
            print("data None " , message)
        # print(data)
        # if data and isinstance(data, list):
        #     if data[1] == 'ohlc':
        #         candles = data[2]
        #         for candle in candles:
        #             print(f"Symbol: {candle['symbol']}, Open: {candle['open']}, High: {candle['high']}, Low: {candle['low']}, Close: {candle['close']}, Volume: {candle['volume']}, Timestamp: {candle['interval_begin']}")

    def on_error(self, ws, error):
        """Handle errors"""
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"Closed: {close_msg}")

    def on_open(self, ws):
        """Send subscribe message when WebSocket opens"""
        # subscribe_message = {
        #     "method": "subscribe",
        #     "params": {
        #         "channel": "ohlc",
        #         "symbol": self.symbols,
        #         "interval": self.interval,
        #         "snapshot": self.snapshot
        #     }
        # }

        subscribe_message ={
            "method": "subscribe",
            "params": {
                "channel": "ohlc",
                "symbol": [
                    "BTC/USD",
                    "MATIC/USD"
                ],
                "interval": 5
            }
        }
        ws.send(json.dumps(subscribe_message))

    def subSymbol(self , symbol , interval , snapshot):
        """Send subscribe message when WebSocket opens"""
        subscribe_message = {
            "method": "subscribe",
            "params": {
                "channel": "ohlc",
                "symbol": symbols,
                "interval": interval,
                "snapshot": snapshot
            }
        }
        self.ws.send(json.dumps(subscribe_message))


    def start(self):
        """Start the WebSocket connection"""
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def stop(self):
        """Close the WebSocket connection"""
        if self.ws:
            self.ws.close()

# Example usage
# if __name__ == "__main__":
#     symbols = ["BTC/USD", "ETH/USD"]
#     kraken_client = KrakenOHLCClient(symbols=symbols, interval=5, snapshot=True)
    
#     # Running WebSocket in a separate thread
#     websocket_thread = threading.Thread(target=kraken_client.start)
#     websocket_thread.start()
    
#     # Stop the WebSocket connection after some time (for example, 30 seconds)
#     import time
#     time.sleep(30)
#     kraken_client.stop()
#     websocket_thread.join()
