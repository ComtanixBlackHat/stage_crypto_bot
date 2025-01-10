import asyncio
import websockets

async def connect():
    uri = "ws://localhost:9002"  # Replace with your WebSocket server address

    async with websockets.connect(uri) as websocket:
        # Send a subscription message
        await websocket.send("sub kraken BTC/USD 1min")

        # Receive and print messages from the server
        while True:
            message = await websocket.recv()
            print("Received:", message)

# Start the WebSocket connection
asyncio.get_event_loop().run_until_complete(connect())
