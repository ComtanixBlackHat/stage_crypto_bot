# bot_routes.py
import logging
from flask import Blueprint, request, jsonify
from app.exchanges.kerkaren.kraken import Kraken
from app.controllers.redisutil import RedisUtility
from app.controllers.crud.positionCrud import PositionCRUD
from app.controllers.crud.tradingpair import TradingPairCrud
import threading
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("OrderLogs"),  # Log to a file named 'bot.log'
        logging.StreamHandler()  # Also print logs to the console (optional)
    ]
)
# class BOT_CONTROLLER:
class BOT_CONTROLLER:
    @staticmethod
    def process(data):
        try:
            logging.info("Received request at /stage-complete")
            logging.debug(f"Request Data: {data}")
            
            # Retrieve basic data from the request and Redis
            symbol = data.get('symbol')
            hitType = data.get('hitType')
            if not symbol or not hitType:
                raise ValueError("Missing 'symbol' or 'hitType' in request data.")
            RedisUtility.set_hash_field("symbol", symbol, "0")
            logging.debug(f"Symbol: {symbol}, Hit Type: {hitType}")
            
            # Get current stage value from Redis
            currentStageKey = symbol + "currentStage"
            currentStageStr = RedisUtility.get_key(currentStageKey)
            if currentStageStr is None:
                raise ValueError(f"Current stage not found in Redis for symbol {symbol}.")
            try:
                currentStage = int(currentStageStr)
            except ValueError as ve:
                raise ValueError(f"Invalid current stage value '{currentStageStr}' for {symbol}: {ve}")
            logging.debug(f"Current Stage: {currentStage}")
            
            # Form stage key and retrieve trading pair id
            stageKey = f"{symbol}{currentStageStr}"
            tradingPairId = RedisUtility.get_key(symbol + "trading_pair_id")
            if tradingPairId is None:
                raise ValueError(f"Trading pair ID not found for symbol {symbol}.")
            logging.debug(f"StageKey: {stageKey}, TRADING_PAIR_ID: {tradingPairId}")
            
            # Retrieve trading parameters from Redis
            tp_val = RedisUtility.get_key(symbol + "take_profit_percentage")
            rb_val = RedisUtility.get_key(symbol + "rebuy_percentage")
            cap_val = RedisUtility.get_key(symbol + "current_capital")
            usage_val = RedisUtility.get_key(symbol + "trade_usage_percentage")
            
            if tp_val is None or rb_val is None or cap_val is None or usage_val is None:
                raise ValueError(f"One or more trading parameters missing in Redis for {symbol}.")
            
            try:
                take_profit_percentage = float(tp_val)
                rebuy_percentage = float(rb_val)
                current_capital = float(cap_val)
                trade_usage_percentage = float(usage_val)
            except ValueError as ve:
                raise ValueError(f"Invalid trading parameter value: {ve}")
            
            logging.debug(f"Take Profit %: {take_profit_percentage}, Rebuy %: {rebuy_percentage}")
            logging.debug(f"Current Capital: {current_capital}, Trade Usage %: {trade_usage_percentage}")
            
            # Calculate the amount in USDT to be used for trading
            priceInUsdt = current_capital * (trade_usage_percentage / 100)
            
            # Route to the correct handler based on hitType
            if hitType == "TakeProfit":
                BOT_CONTROLLER.handle_take_profit(
                    symbol, stageKey, currentStage, tradingPairId,
                    take_profit_percentage, rebuy_percentage,
                    current_capital, trade_usage_percentage, priceInUsdt
                )
            elif hitType == "rebuy":
                BOT_CONTROLLER.handle_rebuy(
                    symbol, stageKey, currentStage, tradingPairId,
                    take_profit_percentage, rebuy_percentage,
                    current_capital, trade_usage_percentage, priceInUsdt
                )
            else:
                logging.warning("Unsupported hitType received")
                return "Unsupported hitType"
            
            logging.info("Waiting for 10 seconds")
            time.sleep(10)
            logging.info("Wait complete")
            
            # Update Redis flag to indicate stage process completion
            RedisUtility.set_hash_field("symbol", symbol, "1")
            logging.info("Stage completion process successful")
            return "Stage completion process successful"
        except Exception as e:
            logging.error(f"Error in stagecomplete: {str(e)}", exc_info=True)
            return "error"
    
    @staticmethod
    def handle_take_profit(symbol, stageKey, currentStage, tradingPairId,
                           take_profit_percentage, rebuy_percentage,
                           current_capital, trade_usage_percentage, priceInUsdt):
        """
        Handle the TakeProfit branch. Adds robust error handling
        for each critical operation.
        """
        try:
            # Attempt to get the volume to sell from Redis
            vol = RedisUtility.get_key(f"{stageKey}amount")
            if vol is None:
                raise ValueError(f"Selling volume not found for {stageKey}.")
            logging.debug(f"Selling Volume: {vol}")
            
            tpOrder = Kraken.send_order(symbol, "sell", vol, "market")
            if "error" in tpOrder and tpOrder["error"]:
                raise ValueError(f"Sell order error: {tpOrder['error']}")
            logging.debug(f"Sell order response: {tpOrder}")
            
            orderDetail = Kraken.orderFillChecker(tpOrder)
            txid = tpOrder["result"]["txid"][0]
            
            if currentStage == 0:
                # Stage 0 logic: process sell order and initiate a new buy order.
                oldCostVal = RedisUtility.get_key(f"{stageKey}cost")
                if oldCostVal is None:
                    raise ValueError(f"Old cost not found for {stageKey}.")
                try:
                    oldCost = float(oldCostVal)
                except ValueError as ve:
                    raise ValueError(f"Invalid old cost '{oldCostVal}': {ve}")
                
                try:
                    cost = float(orderDetail['result'][txid]['cost'])
                    fee = float(orderDetail["result"][txid]["fee"])
                    sellPrice = float(orderDetail["result"][txid]["price"])
                except (KeyError, ValueError) as ve:
                    raise ValueError(f"Error parsing order details: {ve}")
                
                currentCost = cost - fee
                
                oldProfitVal = RedisUtility.get_key(symbol + "profit")
                if oldProfitVal is None:
                    oldProfit = 0.0
                else:
                    try:
                        oldProfit = float(oldProfitVal)
                    except ValueError as ve:
                        raise ValueError(f"Invalid profit value '{oldProfitVal}': {ve}")
                
                profit = currentCost - oldCost
                totalProfit = profit + oldProfit
                RedisUtility.set_key(symbol + "profit", str(totalProfit))
                
                TradingPairCrud.update_trading_pair_money(int(tradingPairId), cost, "+")
                PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, pln=profit, sell_price=sellPrice)
                PositionCRUD.create_old_position(currentStage, int(tradingPairId))
                
                logging.debug(f"Old Capital: {current_capital}")
                current_capital += profit
                current_capital_val = RedisUtility.get_key(symbol + "money")
                if current_capital_val is not None:
                    try:
                        current_capital = float(current_capital_val)
                    except ValueError:
                        logging.warning(f"Invalid current capital value '{current_capital_val}', using computed value.")
                logging.debug(f"New Capital: {current_capital}")
                TradingPairCrud.update_trading_pair_capital(int(tradingPairId), current_capital)
                
                priceInUsdt = current_capital * (trade_usage_percentage / 100)
                currentPrice = Kraken.get_current_price(symbol)
                if currentPrice is None or currentPrice <= 0:
                    raise ValueError(f"Invalid current price for {symbol}: {currentPrice}")
                amount = priceInUsdt / currentPrice
                
                nextBuyOrder = Kraken.send_order(symbol, "buy", amount, "market")
                if "error" in nextBuyOrder and nextBuyOrder["error"]:
                    raise ValueError(f"Buy order error: {nextBuyOrder['error']}")
                logging.debug(f"Buy order response: {nextBuyOrder}")
                txid = nextBuyOrder["result"]["txid"][0]
                orderDetail = Kraken.orderFillChecker(nextBuyOrder)
                logging.debug(f"Buy order detail: {orderDetail}")
                
                try:
                    cost = float(orderDetail['result'][txid]['cost'])
                    fee = float(orderDetail["result"][txid]["fee"])
                except (KeyError, ValueError) as ve:
                    raise ValueError(f"Error parsing buy order details: {ve}")
                
                TradingPairCrud.update_trading_pair_money(int(tradingPairId), cost, "-")
                currentCost = cost - fee
                RedisUtility.set_key(f"{stageKey}cost", str(currentCost))
                
                try:
                    executedAmount = float(orderDetail['result'][txid]['vol_exec'])
                except (KeyError, ValueError) as ve:
                    raise ValueError(f"Error retrieving executed volume: {ve}")
                
                try:
                    currentPrice = float(orderDetail["result"][txid]["price"])
                except (KeyError, ValueError) as ve:
                    raise ValueError(f"Error retrieving current price from order details: {ve}")
                
                takeProfitPrice = currentPrice * (1 + take_profit_percentage / 100)
                rebuyPrice = currentPrice * (1 - rebuy_percentage / 100)
                
                # Update Redis with new trade parameters
                RedisUtility.set_key(f"{stageKey}buy_price", str(rebuyPrice))
                RedisUtility.set_key(f"{stageKey}current_buy_price", str(currentPrice))
                RedisUtility.set_key(f"{stageKey}sell_price", str(takeProfitPrice))
                RedisUtility.set_key(f"{stageKey}amount", str(executedAmount))
                
                PositionCRUD.update_position_by_symbol_and_stage(
                    symbol, 0,
                    buy_price=rebuyPrice,
                    current_buy_price=currentPrice,
                    sell_price=takeProfitPrice,
                    amount=executedAmount,
                    status="Open"
                )
            elif currentStage > 0:
                try:
                    cost = float(orderDetail['result'][txid]['cost'])
                    price = float(orderDetail['result'][txid]['price'])
                except (KeyError, ValueError) as ve:
                    raise ValueError(f"Error parsing order details for stage > 0: {ve}")
                
                oldCostVal = RedisUtility.get_key(f"{stageKey}cost")
                if oldCostVal is None:
                    raise ValueError(f"Old cost not found for {stageKey} in stage > 0 branch.")
                try:
                    oldCost = float(oldCostVal)
                except ValueError as ve:
                    raise ValueError(f"Invalid old cost '{oldCostVal}': {ve}")
                
                profit = cost - oldCost
                oldProfitVal = RedisUtility.get_key(symbol + "profit")
                if oldProfitVal is None:
                    oldProfit = 0.0
                else:
                    try:
                        oldProfit = float(oldProfitVal)
                    except ValueError as ve:
                        raise ValueError(f"Invalid profit value '{oldProfitVal}': {ve}")
                
                totalProfit = profit + oldProfit
                RedisUtility.set_key(symbol + "profit", str(totalProfit))
                
                PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, pln=profit, sell_price=price)
                TradingPairCrud.update_trading_pair_money(int(tradingPairId), cost, "+")
                logging.info(f"Setting current Stage {currentStage} to Close")
                PositionCRUD.create_old_position(currentStage, int(tradingPairId))
                PositionCRUD.delatePos(RedisUtility.get_key(symbol + "trading_pair_id"), currentStage)
                
                prevStage = currentStage - 1
                RedisUtility.set_key(symbol + "currentStage", str(prevStage))
                PositionCRUD.update_position_by_symbol_and_stage(symbol, prevStage, status="Open")
        except Exception as e:
            logging.error(f"Error in handle_take_profit: {str(e)}", exc_info=True)
            raise e

    @staticmethod
    def handle_rebuy(symbol, stageKey, currentStage, tradingPairId,
                     take_profit_percentage, rebuy_percentage,
                     current_capital, trade_usage_percentage, priceInUsdt):
        """
        Handle the rebuy branch with additional error handling:
          - Increase the stage.
          - Execute a buy order.
          - Update positions and trading pair money accordingly.
        """
        try:

            
            nextStage = currentStage + 1
            currentPrice = Kraken.get_current_price(symbol)
            if currentPrice is None or currentPrice <= 0:
                raise ValueError(f"Invalid current price for {symbol}: {currentPrice}")
            oldProfitVal = RedisUtility.get_key(symbol + "profit")
            if oldProfitVal is None:
                oldProfit = 0.0
            else:
                try:
                    oldProfit = float(oldProfitVal)
                except ValueError as ve:
                    raise ValueError(f"Invalid profit value '{oldProfitVal}': {ve}")
            
            priceInUsdt += oldProfit
            amount = priceInUsdt / currentPrice
            
            nextBuyOrder = Kraken.send_order(symbol, "buy", amount, "market")
            if "error" in nextBuyOrder and nextBuyOrder["error"]:
                raise ValueError(f"Buy order error: {nextBuyOrder['error']}")
            logging.debug(f"Rebuy order response: {nextBuyOrder}")
            txid = nextBuyOrder["result"]["txid"][0]
            orderDetail = Kraken.orderFillChecker(nextBuyOrder)
            logging.debug(f"Rebuy order detail: {orderDetail}")
            
            try:
                currentPrice = float(orderDetail["result"][txid]["price"])
                cost = float(orderDetail['result'][txid]['cost'])
            except (KeyError, ValueError) as ve:
                raise ValueError(f"Error parsing rebuy order details: {ve}")
            100.502
            TradingPairCrud.update_trading_pair_money(int(tradingPairId), cost, "-")
            stageKeyNext = f"{symbol}{nextStage}"
            RedisUtility.set_key(f"{stageKeyNext}cost", str(cost))
            
            takeProfitPrice = currentPrice * (1 + take_profit_percentage / 100)
            rebuyPrice = currentPrice * (1 - rebuy_percentage / 100)
            
            RedisUtility.set_key(symbol + "currentStage", str(nextStage))
            try:
                executedAmount = float(orderDetail['result'][txid]['vol_exec'])
            except (KeyError, ValueError) as ve:
                raise ValueError(f"Error retrieving executed volume: {ve}")
            
            PositionCRUD.create_position(
                nextStage, tradingPairId, symbol, rebuyPrice, currentPrice,
                executedAmount, "Open", takeProfitPrice, 0.0, orderDetail
            )
            PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, status="Waiting")
        except Exception as e:
            logging.error(f"Error in handle_rebuy: {str(e)}", exc_info=True)
            raise e
    # @staticmethod
    # def process2(data):
    #     try:

    #         # time.sleep(5)
    #         logging.info("Received request at /stage-complete")

    #         logging.debug(f"***************************\nRequest Data: {data}\n\n")
            
    #         symbol = data.get('symbol')
    #         hitType = data.get('hitType')
    #         RedisUtility.set_hash_field("symbol" , symbol , "0")
    #         logging.debug(f"Symbol: {symbol}, Hit Type: {hitType}")
            
    #         currentStageKey = symbol + "currentStage"
    #         print(currentStageKey)
    #         currentStageStr = RedisUtility.get_key(currentStageKey)
    #         print(currentStageStr)
    #         currentStage = int(currentStageStr)
    #         logging.debug(f"Current Stage: {currentStage}")
            
    #         StageKey = f"{symbol}{currentStageStr}"
    #         # TRADING_PAIR_ID = RedisUtility.get_key(f"{StageKey}currentStageId")
    #         TRADING_PAIR_ID = RedisUtility.get_key(symbol+"trading_pair_id")
    #         # name+"trading_pair_id" 

    #         logging.debug(f"StageKey: {StageKey}, TRADING_PAIR_ID: {TRADING_PAIR_ID}")

            
    #         take_profit_percentage = float(RedisUtility.get_key(symbol + "take_profit_percentage"))
    #         rebuy_percentage = float(RedisUtility.get_key(symbol + "rebuy_percentage"))
    #         current_capital = float(RedisUtility.get_key(symbol + "current_capital"))
    #         trade_usage_percentage = float(RedisUtility.get_key(symbol + "trade_usage_percentage"))
            
    #         logging.debug(f"Take Profit %: {take_profit_percentage}, Rebuy %: {rebuy_percentage}")
    #         logging.debug(f"Current Capital: {current_capital}, Trade Usage %: {trade_usage_percentage}")
            
    #         # take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
    #         # rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
    #         priceInUsdt = current_capital * (trade_usage_percentage / 100)

    #         if hitType == "TakeProfit":
    #             if currentStage == 0:
    #                 nextStage = 0

    #                 vol = RedisUtility.get_key(f"{StageKey}amount")
    #                 print("Selling Volume " ,vol ) 
                    
    #                 tpOrder = Kraken.send_order(symbol, "sell" , vol , "market")
    #                 logging.debug(f"Takeprofit stage sell order Response : {tpOrder}")
    #                 # tpOrder ={'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'sell 9.83280004 ADAUSD @ market'}}}
    #                 print("take profit Order = " ,tpOrder)
    #                 txid = tpOrder["result"]["txid"][0]
    #                 # orderDetail = 
    #                 orderDetail = Kraken.orderFillChecker(tpOrder)
    #                 logging.debug(f"Takeprofit stage order Detail:  {orderDetail}")
    #                 Oldcost = float(RedisUtility.get_key(f"{StageKey}cost")) #price bought
                    
    #                 cost = float(orderDetail['result'][txid]['cost'])
                    
    #                 fee = float(orderDetail["result"][txid]["fee"])
    #                 sellprice= float(orderDetail["result"][txid]["price"])
    #                 CurrentCoast = cost - fee #price sold

    #                 oldProfit = float(RedisUtility.get_key(symbol+"profit"))
    #                 _profit = (CurrentCoast - Oldcost)+oldProfit 
    #                 RedisUtility.set_key(symbol+"profit" , str(_profit))
                    
                    
    #                 TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "+")                
                    
    #                 profit =   CurrentCoast - Oldcost  #sold price - buy price
                   
    #                 # PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit) 
    #                 PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit , sell_price =sellprice) 
    #                 PositionCRUD.create_old_position(currentStage , int( TRADING_PAIR_ID) )
    #                 print("Old Capital : ",current_capital)
    #                 current_capital = current_capital +profit # added to the capital
    #                 current_capital = float(RedisUtility.get_key(symbol+"money"))
    #                 print("New Capital : ",current_capital)
    #                 TradingPairCrud.update_trading_pair_capital(int(TRADING_PAIR_ID) , float(current_capital))
                    
    #                 priceInUsdt = current_capital * (trade_usage_percentage / 100)
    #                 currentPrice = Kraken.get_current_price(symbol)  
                
    #                 amount = priceInUsdt / currentPrice



                    

    #                 nextbuyOrder = Kraken.send_order(symbol, "buy" , amount , "market")

    #                 logging.debug(f"Takeprofit stage order Detail:  {nextbuyOrder }")
    #                 txid = nextbuyOrder["result"]["txid"][0]

    #                 orderDetail = Kraken.orderFillChecker(nextbuyOrder)
    #                 logging.debug(f"Takeprofit stage 0  buy order Response : {orderDetail}")
                    
    #                 newOrderKey = list(orderDetail['result'].keys())[0]  # Get the first order key
    #                 # cost = orderDetail['result'][order_key]['cost']
    #                 cost = float(orderDetail['result'][txid]['cost'])
    #                 fee = float(orderDetail["result"][txid]["fee"])
    #                 TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "-")
    #                 CurrentCoast = cost - fee
    #                 RedisUtility.set_key(f"{StageKey}cost", str(CurrentCoast))

    #                 # StageKey = f"{name}0"
                    
    #                 amount =float(orderDetail['result'][txid]['vol_exec'])
                    
    #                 # orderDetail  = Kraken.query_orders(txid, trades, userref, consolidate_taker)
    #                 currentPrice = float(orderDetail["result"][newOrderKey]["price"])  # Extract the price
                    
                    
    #                 # currentPrice  = Kraken.get_current_price(symbol) # remove

    #                 take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
    #                 rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
    #                 take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
    #                 rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
    #                 currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price

    #                 RedisUtility.set_key(f"{StageKey}buy_price", str( rebuy_price ))
    #                 RedisUtility.set_key(f"{StageKey}current_buy_price", str(currentPrice))  # New Redis entry
    #                 RedisUtility.set_key(f"{StageKey}sell_price", str(take_profit_price))
    #                 RedisUtility.set_key(f"{StageKey}amount", str(amount))

    #                 PositionCRUD.update_position_by_symbol_and_stage(
    #                     symbol, 0, buy_price=rebuy_price, current_buy_price=currentPrice, 
    #                     sell_price=take_profit_price, amount=amount,status="Open")
    #             elif currentStage > 0:
                    
    #                 vol = RedisUtility.get_key(f"{StageKey}amount")
    #                 tpOrder = Kraken.send_order(symbol, "sell" , vol , "market")
    #                 logging.debug(f"Takeprofit stage order Detail:  {tpOrder}")
    #                 orderDetail = Kraken.orderFillChecker(tpOrder)
    #                 logging.debug(f"Takeprofit stage order Detail:  {orderDetail}")
    #                 txid = tpOrder["result"]["txid"][0]
    #                 cost = float(orderDetail['result'][txid]['cost'])
    #                 price = float(orderDetail['result'][txid]['price'])
                    
    #                 print(f"OLD COST {RedisUtility.get_key(f"{StageKey}cost")}")
    #                 Oldcost = float(RedisUtility.get_key(f"{StageKey}cost")) #price bought
                    
    #                 profit = cost - Oldcost
    #                 oldProfit = float(RedisUtility.get_key(symbol+"profit"))
    #                 _profit = profit + oldProfit
    #                 RedisUtility.set_key(symbol+"profit" , str(_profit))

                    
    #                 PositionCRUD.update_position_by_symbol_and_stage(symbol , currentStage , pln=profit , sell_price =price) 
    #                 TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "+")                
                    
    #                 # tpOrder = {'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'sell 9.83280004 ADAUSD @ market'}}}
    #                 logging.info(f"Setting Cuurent Stage {currentStage} to Close")
    #                 # PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, status="Closed")
    #                 PositionCRUD.create_old_position(currentStage , int( TRADING_PAIR_ID) )
    #                 PositionCRUD.delatePos(RedisUtility.get_key(symbol+"trading_pair_id") , currentStage)
                    
    #                 prevStage = currentStage - 1
    #                 RedisUtility.set_key(symbol + "currentStage", str(prevStage))
    #                 print("current Stage in take profit " , )
    #                 PositionCRUD.update_position_by_symbol_and_stage(symbol, prevStage, status="Open")
    #         elif hitType == "rebuy":
    #             nextStage = currentStage + 1

    #             currentPrice = Kraken.get_current_price(symbol)
    #             oldProfit = float(RedisUtility.get_key(symbol+"profit"))
                
    #             priceInUsdt = priceInUsdt+oldProfit
    #             amount = priceInUsdt / currentPrice
    #             # nextbuyOrder = {'error': [], 'result': {'txid': ['OTEJ3V-PUM36-IC6DXW'], 'descr': {'order': 'buy 9.83280004 ADAUSD @ market'}}}
    #             nextbuyOrder = Kraken.send_order(symbol, "buy" , amount , "market")
    #             logging.debug(f"Takeprofit stage order Detail:  {nextbuyOrder}")

    #             txid = nextbuyOrder["result"]["txid"][0]

    #             orderDetail = Kraken.orderFillChecker(nextbuyOrder)
    #             logging.debug(f"Takeprofit stage order Detail:  {orderDetail}")
    #             currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price

    #             cost = float(orderDetail['result'][txid]['cost'])
    #             TradingPairCrud.update_trading_pair_money(int(TRADING_PAIR_ID), cost , "-")                
                
    #             # RedisUtility.set_key(f"{StageKey}cost", str(cost))
    #             stage_ = f"{symbol}{nextStage}"
    #             RedisUtility.set_key(f"{stage_}cost", str(cost))
    #             take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
    #             rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
    #             take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
    #             rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
    #             # currentPrice = float(orderDetail["result"][txid]["price"])  # Extract the price
                
    #             RedisUtility.set_key(symbol + "currentStage", str(nextStage))
    #             amount =float(orderDetail['result'][txid]['vol_exec'])
    #             PositionCRUD.create_position(
    #                 nextStage, TRADING_PAIR_ID, symbol, rebuy_price, currentPrice, amount, "Open", take_profit_price, 0.0, orderDetail
    #             )    
    #             PositionCRUD.update_position_by_symbol_and_stage(symbol, currentStage, status="Waiting")
                
    #         else:
    #             logging.warning("Unsupported hitType received")
    #             # return jsonify({'error': 'Unsupported hitType'}), 400
    #             return 'Unsupported hitType'
    #         print("waiting for 10 secounds")
    #         time.sleep(10)
    #         print("wait complete for 10 secounds")
    #         RedisUtility.set_hash_field("symbol" , symbol , "1")
    #         logging.info("Stage completion process successful")
    #         return "Stage completion process successful"
    #         # return jsonify({'success': True})
    #     except Exception as e:
    #         logging.error(f"Error in stagecomplete: {str(e)}", exc_info=True)
    #         return "error"
    #         # return jsonify({"error": str(e)}), 500
