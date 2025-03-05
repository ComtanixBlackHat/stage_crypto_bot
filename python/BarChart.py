
import asyncio
import websockets
import json
import threading
from app.util.Util import UTIL 
from app.util.Constant import CONSTANT , BaseURL
from app.exchanges.kerkaren.webSocketClient import KrakenOHLCClient
from app.exchanges.binancne.websocketClient import BinanceOHLCClient
from app.controllers.redisutil import RedisUtility
connected_clients = {}

async def server(websocket):
    print("Client connected")
    try:
        # Receive message from the client
        webSocket_message = await websocket.recv()
        message_object = json.loads(webSocket_message)
        print(webSocket_message)
        
        # Extract token and accountType from the message
        token = message_object.get("token")
        accountType = message_object.get("accountType")

        if token is not None and accountType is not None:
            userId = "1"
            if userId is not None:
                connected_clients[websocket] = {"userId": userId, "accountType": accountType, "streams": []}
                await handle_successful_connection(websocket)
                print("Authenticated")
                async for message in websocket:
                    try:
                        subMessage = json.loads(message)
                        print(f"New Message {message}")

                        if websocket in connected_clients:
                            client = connected_clients[websocket]
                            interval = subMessage.get("interval")
                            symbol = subMessage.get("symbol")
                            unit = subMessage.get("unit")
                            barsback = subMessage.get("barsback")
                            chartType = subMessage.get("chartType")
                            subtype = subMessage.get("type")
                            socketId = subMessage.get("socketid")
                            # accountType = client["accountType"]
                            userId = client["userId"]
                           
                            key = f"{userId}{UTIL.generate_random_string(20)}"
                            if interval is not None and unit is not None and socketId is not None and barsback is not None and symbol is not None and chartType is not None and userId is not None and subtype is not None:  
                                if not any(optionChain["streamid"] == key for optionChain in client["streams"]):
                                    try:
                                        print("Connected")
                                        print(await websocket.ping())
                                        # symbols = ["BTCUSDT", "ETHUSDT"]  # Binance pairs
                                        symbols = RedisUtility.get_all_hash_fields("symbol")
                                        symbolList = []
                                        print("symbols" , symbols)
                                        for key in symbols.keys():
                                            # print(key)
                                            print(key)
                                            symbolList.append(key)                                        
                                        binance_client = BinanceOHLCClient(websocket,symbols=symbols, interval=5)

                                        # Running WebSocket in a separate thread
                                        websocket_thread = threading.Thread(target=binance_client.start)
                                        websocket_thread.start()

                                        import time
                                        time.sleep(30)
                                        binance_client.stop()
                                        websocket_thread.join()

                                        
                                    except Exception as e:
                                        print(f"fail to get option chain of {symbol} {e}")
                                else:
                                    print("Stream Found")
                            else:
                                
                                await websocket.send(json.dumps({"error": "Invalid Message"}))        
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({"error": "Invalid JSON format"}))
                        print("Invalid JSON format")
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected")
        await handle_client_disconnection(websocket, "Disconnected")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed unexpectedly")
        await handle_client_disconnection(websocket, "Connection closed unexpectedly")
    except Exception as e:
        print(f"Error: {e}")
        await handle_client_disconnection(websocket, "Error occurred")

async def handle_successful_connection(websocket):
    try:
        message = {"message": "Connected"}
        await websocket.send(json.dumps(message))
    except websockets.exceptions.ConnectionClosedError:
        print("Client disconnected")
        await handle_client_disconnection(websocket, "Disconnected")

async def handle_client_disconnection(websocket, message):
    if websocket in connected_clients:
        for stream in connected_clients["streams"]:
            TradStationStream = stream.get("streamObj")
            TradStationStream.setEndStream(True) 
        del connected_clients[websocket]
        print("Deleted\n")
    try:
        await websocket.send(json.dumps({"message": message}))
        await websocket.close()
    except:
        print("Connection Closed")

async def start_server():
    server_address = "0.0.0.0"
    port = BaseURL.BAR_CHART_SERVER_PORT

    async with websockets.serve(server, server_address, port):
        print(f"WebSocket server started at ws://{server_address}:{port}")
        await asyncio.Future()

# Run the WebSocket server
asyncio.run(start_server())