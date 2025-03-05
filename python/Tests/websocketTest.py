import asyncio
import websockets
import json

async def connect_to_server():
    uri = "ws://localhost:9001"  # Replace <PORT> with the actual port
    async with websockets.connect(uri) as websocket:
        # Authentication message
        auth_message = {
            "token": "your_auth_token",
            "accountType": "your_account_type"
        }
        await websocket.send(json.dumps(auth_message))
        print("Sent authentication message")

        # Wait for server response
        response = await websocket.recv()
        print(f"Received: {response}")

        # Subscription message
        sub_message = {
            "symbol": "BTCUSDT",
            "interval": 5,
            "unit": "minutes",
            "barsback": 50,
            "chartType": "candlestick",
            "type": "subscribe",
            "socketid": "your_unique_socket_id"
        }
        await websocket.send(json.dumps(sub_message))
        print("Sent subscription message")

        # Listen for responses
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

# Run the client
asyncio.run(connect_to_server())
