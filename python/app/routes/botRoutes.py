# bot_routes.py
import logging
from flask import Blueprint, request, jsonify
from app.exchanges.kerkaren.kraken import Kraken
from app.controllers.redisutil import RedisUtility
from app.controllers.crud.positionCrud import PositionCRUD
from app.controllers.crud.tradingpair import TradingPairCrud
import time
# from app.controllers
botRoutes = Blueprint('botRoutes', __name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Log to a file named 'bot.log'
        logging.StreamHandler()  # Also print logs to the console (optional)
    ]
)
@botRoutes.route('/stage-complete', methods=['POST'])
def stagecomplete():
    try:

        # time.sleep(5)
        logging.info("Received request at /stage-complete")
        
        # Get data from the request JSON payload
        data = request.get_json()
        logging.debug(f"***************************Request Data: {data}\n\n")
        
        symbol = data.get('symbol')
        hitType = data.get('hitType')
        RedisUtility.set_hash_field("symbol" , symbol , "0")
        logging.debug(f"Symbol: {symbol}, Hit Type: {hitType}")
        
        currentStageKey = symbol + "currentStage"
        print(currentStageKey)
        currentStageStr = RedisUtility.get_key(currentStageKey)
        print(currentStageStr)
        print(type(currentStageStr))
        currentStage = int(currentStageStr)
        logging.debug(f"Current Stage: {currentStage}")
        
        StageKey = f"{symbol}{currentStageStr}"
        # TRADING_PAIR_ID = RedisUtility.get_key(f"{StageKey}currentStageId")
        TRADING_PAIR_ID = RedisUtility.get_key(symbol+"trading_pair_id")
        # name+"trading_pair_id" 

        logging.debug(f"StageKey: {StageKey}, TRADING_PAIR_ID: {TRADING_PAIR_ID}")

        
        take_profit_percentage = float(RedisUtility.get_key(symbol + "take_profit_percentage"))
        rebuy_percentage = float(RedisUtility.get_key(symbol + "rebuy_percentage"))
        current_capital = float(RedisUtility.get_key(symbol + "current_capital"))
        trade_usage_percentage = float(RedisUtility.get_key(symbol + "trade_usage_percentage"))
        
        logging.debug(f"Take Profit %: {take_profit_percentage}, Rebuy %: {rebuy_percentage}")
        logging.debug(f"Current Capital: {current_capital}, Trade Usage %: {trade_usage_percentage}")
        
        # take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
        # rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
        priceInUsdt = current_capital * (trade_usage_percentage / 100)
        # amount = priceInUsdt / currentPrice
        
        # logging.info(f"Calculated Prices - Take Profit: {take_profit_price}, Rebuy: {rebuy_price}, Amount: {amount}")
        
        if hitType == "TakeProfit":
            if currentStage == 0:
                nextStage = 0

                vol = RedisUtility.get_key(f"{StageKey}amount")
                print("Selling Volume " ,vol ) 
                
                tpOrder = Kraken.send_order(symbol, "sell" , vol , "market")
                
                # tpOrder ={'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'sell 9.83280004 ADAUSD @ market'}}}
                print("take profit Order = " ,tpOrder)
                txid = tpOrder["result"]["txid"][0]
                # orderDetail = 
                orderDetail = Kraken.orderFillChecker(tpOrder)
                
                Oldcost = float(RedisUtility.get_key(f"{StageKey}cost")) #price bought
                
                cost = float(orderDetail['result'][txid]['cost'])
                
                fee = float(orderDetail["result"][txid]["fee"])
                sellprice= float(orderDetail["result"][txid]["price"])
                CurrentCoast = cost - fee #price sold
                TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "+")                
                


                print("cost = " , cost)
                print("fee = " , fee)
                print("Current Cost : ",CurrentCoast)
                print("Old Cost : ",Oldcost)
                profit =   CurrentCoast - Oldcost  #sold price - buy price
                print("Profit : ",profit)
                # PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit) 
                PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit , sell_price =sellprice) 
                PositionCRUD.create_old_position(currentStage , int( TRADING_PAIR_ID) )
                print("Old Capital : ",current_capital)
                current_capital = current_capital +profit # added to the capital
                current_capital = float(RedisUtility.get_key(symbol+"money"))
                print("New Capital : ",current_capital)
                TradingPairCrud.update_trading_pair_capital(int(TRADING_PAIR_ID) , float(current_capital))
                
                priceInUsdt = current_capital * (trade_usage_percentage / 100)
                currentPrice = Kraken.get_current_price(symbol)  
               
                amount = priceInUsdt / currentPrice



                # nextbuyOrder = {'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'buy 9.83280004 ADAUSD @ market'}}}
                nextbuyOrder = Kraken.send_order(symbol, "buy" , amount , "market")

                txid = nextbuyOrder["result"]["txid"][0]

                orderDetail = Kraken.orderFillChecker(nextbuyOrder)
                
                newOrderKey = list(orderDetail['result'].keys())[0]  # Get the first order key
                # cost = orderDetail['result'][order_key]['cost']
                cost = float(orderDetail['result'][txid]['cost'])
                fee = float(orderDetail["result"][txid]["fee"])
                TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "-")
                CurrentCoast = cost - fee
                RedisUtility.set_key(f"{StageKey}cost", str(CurrentCoast))

                # StageKey = f"{name}0"
                
                amount =float(orderDetail['result'][txid]['vol_exec'])
                
                # orderDetail  = Kraken.query_orders(txid, trades, userref, consolidate_taker)
                currentPrice = float(orderDetail["result"][newOrderKey]["price"])  # Extract the price
                
                
                # currentPrice  = Kraken.get_current_price(symbol) # remove

                take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
                rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
                take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
                rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
                currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price

                RedisUtility.set_key(f"{StageKey}buy_price", str( rebuy_price ))
                RedisUtility.set_key(f"{StageKey}current_buy_price", str(currentPrice))  # New Redis entry
                RedisUtility.set_key(f"{StageKey}sell_price", str(take_profit_price))
                RedisUtility.set_key(f"{StageKey}amount", str(amount))

                PositionCRUD.update_position_by_symbol_and_stage(
                    symbol, 0, buy_price=rebuy_price, current_buy_price=currentPrice, 
                    sell_price=take_profit_price, amount=amount,status="Open")
            elif currentStage > 0:
                
                vol = RedisUtility.get_key(f"{StageKey}amount")
                tpOrder = Kraken.send_order(symbol, "sell" , vol , "market")
                orderDetail = Kraken.orderFillChecker(tpOrder)
                txid = tpOrder["result"]["txid"][0]
                cost = float(orderDetail['result'][txid]['cost'])
                price = float(orderDetail['result'][txid]['price'])
                
                print(f"OLD COST {RedisUtility.get_key(f"{StageKey}cost")}")
                Oldcost = float(RedisUtility.get_key(f"{StageKey}cost")) #price bought
                
                profit = cost - Oldcost
                PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit , sell_price =price) 
                TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "+")                
                
                # tpOrder = {'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'sell 9.83280004 ADAUSD @ market'}}}
                logging.info(f"Setting Cuurent Stage {currentStage} to Close")
                # PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, status="Closed")
                PositionCRUD.create_old_position(currentStage , int( TRADING_PAIR_ID) )
                PositionCRUD.delatePos(RedisUtility.get_key(symbol+"trading_pair_id") , currentStage)
                
                prevStage = currentStage - 1
                RedisUtility.set_key(symbol + "currentStage", str(prevStage))
                print("current Stage in take profit " , )
                PositionCRUD.update_position_by_symbol_and_stage(symbol, prevStage, status="Open")
        elif hitType == "rebuy":
            nextStage = currentStage + 1

            currentPrice = Kraken.get_current_price(symbol)
               
            amount = priceInUsdt / currentPrice
            # nextbuyOrder = {'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'buy 9.83280004 ADAUSD @ market'}}}
            nextbuyOrder = Kraken.send_order(symbol, "buy" , amount , "market")

            txid = nextbuyOrder["result"]["txid"][0]
            # trades = data.get('trades', False)  # Whether or not to include trades related to the position
            # userref = data.get('userref', None)  # Optional user reference ID
            # consolidate_taker = data.get('consolidate_taker', True)  # Whether or not to consolidate taker trades
                # orderDetail = Kraken.query_orders(txid)
            orderDetail = Kraken.orderFillChecker(nextbuyOrder)
            # orderDetail  = Kraken.query_orders(txid, trades, userref, consolidate_taker)
            currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price
            # currentPrice  = float(Kraken.get_current_price(symbol)) # remove 
                            # orderDetail = Kraken.orderFillChecker(tpOrder)
            cost = float(orderDetail['result'][txid]['cost'])
            TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "-")                
            
            # RedisUtility.set_key(f"{StageKey}cost", str(cost))
            stage_ = f"{symbol}{nextStage}"
            RedisUtility.set_key(f"{stage_}cost", str(cost))
            take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
            rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
            take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
            rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
            # currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price
            
            RedisUtility.set_key(symbol + "currentStage", str(nextStage))
            amount =float(orderDetail['result'][txid]['vol_exec'])
            PositionCRUD.create_position(
                nextStage, TRADING_PAIR_ID, symbol, rebuy_price, currentPrice, amount, "Open", take_profit_price, 0.0, orderDetail
            )    
            PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, status="Waiting")
            
        else:
            logging.warning("Unsupported hitType received")
            return jsonify({'error': 'Unsupported hitType'}), 400
        RedisUtility.set_hash_field("symbol" , symbol , "1")
        logging.info("Stage completion process successful")
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error in stagecomplete: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@botRoutes.route('/query_orders/<exchanges>', methods=['POST'])
def query_orders_route(exchanges):
    try:
        # Get data from the request JSON payload
        data = request.get_json()

        # Extract parameters from the request data
        txid = data.get('txid')  # Kraken order identifier(s)
        trades = data.get('trades', False)  # Whether or not to include trades related to the position
        userref = data.get('userref', None)  # Optional user reference ID
        consolidate_taker = data.get('consolidate_taker', True)  # Whether or not to consolidate taker trades

        if not txid:
            return jsonify({"error": "Missing txid parameter"}), 400

        # Call the query_orders method from the Kraken class
        if exchanges.lower() == 'kraken':
            response = Kraken.query_orders(txid, trades, userref, consolidate_taker)
            print(response)
        else:
            response = {'error': 'Unsupported exchange'}
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
