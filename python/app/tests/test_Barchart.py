import asyncio
import websockets
import json

async def connect_and_subscribe():
    # Replace with your server URL and port
    server_url = "ws://localhost:9001"  # Replace <PORT> with your WebSocket server port

    try:
        async with websockets.connect(server_url) as websocket:
            print("Connected to WebSocket server")

            # Step 1: Authentication message
            auth_message = {
                "token": "your_token",  # Replace with your valid token
                "accountType": "your_account_type"  # Replace with your account type
            }
            
            await websocket.send(json.dumps(auth_message))
            print(f"Sent authentication message: {auth_message}")

            # Wait for the authentication response
            auth_response = await websocket.recv()
            print(f"Authentication response: {auth_response}")

            # Check if authentication was successful
            auth_response_data = json.loads(auth_response)
            if auth_response_data.get("message") == "Connected":
                print("Authentication successful!")

                # Step 2: Subscription message
                subscription_message = {
                    "interval": "1m",  # Replace with your interval
                    "symbol": "AAPL",  # Replace with your symbol
                    "unit": "1",  # Replace with your unit
                    "barsback": "100",  # Replace with your barsback value
                    "chartType": "line",  # Replace with your chart type
                    "type": "subscribe",  # Message type
                    "socketid": "12345"  # Replace with a unique socket ID
                }

                await websocket.send(json.dumps(subscription_message))
                print(f"Sent subscription message: {subscription_message}")

                # Step 3: Handle server responses
                while True:
                    try:
                        response = await websocket.recv()
                        print(f"Received: {response}")
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed by the server")
                        break
            else:
                print("Authentication failed! Check your token or account type.")
    except Exception as e:
        print(f"Error: {e}")

# Run the client
asyncio.run(connect_and_subscribe())
