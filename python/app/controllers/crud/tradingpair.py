from datetime import datetime
from app import db
from app.models import TradingPair
from app.controllers.crud.positionCrud import PositionCRUD
from app.controllers.redisutil import RedisUtility
from app.exchanges.kerkaren.kraken import Kraken

class TradingPairCrud:
    @staticmethod
    def create_trading_pair(name, initial_capital, current_capital, current_stage, 
                            take_profit_percentage, rebuy_percentage, trade_usage_percentage, 
                            status="Active", user_id=1):
        """
        Create a new TradingPair entry.
        """
        # curentStage = ;
        # RedisUtility.set
        print(str(0))
        symbol = name
        name = name.replace("/", "")
        RedisUtility.set_key(name+"StreamSymbol" , symbol)
        RedisUtility.set_key(name+"currentStage" , str(0))
        RedisUtility.set_key(name+"initial_capital" ,initial_capital)
        RedisUtility.set_key(name+"current_capital" ,current_capital)
        RedisUtility.set_key(name+"take_profit_percentage" , take_profit_percentage)
        RedisUtility.set_key(name+"rebuy_percentage" , rebuy_percentage)
        RedisUtility.set_key(name+"status" , status)
        RedisUtility.set_key(name+"money" , initial_capital)
        # RedisUtility.set_key(name+"takeProfitPrice" , status)
        # RedisUtility.set_key(name+"reBuyPrice" , status)
        RedisUtility.set_key(name+"trade_usage_percentage" , trade_usage_percentage)

        new_trading_pair = TradingPair(
            name=name,
            initial_capital=initial_capital,
            current_capital=current_capital,
            start_capital= current_capital,
            currentStage=current_stage,
            take_profit_percentage=take_profit_percentage,
            rebuy_percentage=rebuy_percentage,
            trade_usage_percentage=trade_usage_percentage,
            status=status,
            start_date=datetime.utcnow(),
            user_id=user_id
        )
        db.session.add(new_trading_pair)
        db.session.commit()
        print(new_trading_pair)

        take_profit_percentage = float(take_profit_percentage)
        rebuy_percentage = float(rebuy_percentage)
         # Convert inputs to float to avoid type errors
        current_capital = float(current_capital)
        trade_usage_percentage = float(trade_usage_percentage)        
        
        priceInUsdt = current_capital * (trade_usage_percentage / 100) 
        currentPrice = Kraken.get_current_price(name)
        ammount = priceInUsdt/currentPrice
        print("volume : " , ammount)
        print("name" , name)
        # ammount="505.3059747400"
        data = Kraken.send_order(name , "buy" , str(ammount) , "market")
        # print(data)
        # data = {'error': [], 'result': {'txid': ['ODLRQD-FQPCC-T7WVUE'], 'descr': {'order': 'buy 12.30593539 ADAUSD @ market'}}}
        txid = data["result"]["txid"][0]  # Get the first transaction ID
        print(txid)


        orderDetail = Kraken.orderFillChecker(data)

        print(orderDetail)
        print("+++++++++++++++++++++++++++++++++++++++++")
        
        order_id = list(orderDetail ["result"].keys())[0]  # Get the first order key
        currentPrice = float(orderDetail["result"][order_id]["price"])  # Extract the price
        quantity = float(orderDetail["result"][order_id]["vol"])  # Extract the price
        cost = float(orderDetail['result'][txid]['cost'])
        
        print(f"Cost : {cost}" , type(cost) )
        TradingPairCrud.update_trading_pair_money(new_trading_pair.id, cost , "-")
        
        fee = float(orderDetail["result"][order_id]["fee"])
        finalCoast = str(cost - fee)
        StageKey = f"{name}0"
        RedisUtility.set_key(f"{StageKey}cost", finalCoast)
        print(currentPrice)


        # Print values and their types for debugging
        print("current_capital:", current_capital, "| Type:", type(current_capital))
        print("trade_usage_percentage:", trade_usage_percentage, "| Type:", type(trade_usage_percentage))


        # return priceInUsdt
        take_profit_price = currentPrice * (1 + take_profit_percentage / 100)
        rebuy_price = currentPrice * (1 - rebuy_percentage / 100)
        priceInUsdt = current_capital * (trade_usage_percentage / 100)
        ammount = priceInUsdt/currentPrice

        
        
        
        new_trading_pair_id = new_trading_pair.id  
        RedisUtility.set_key(name+"trading_pair_id" , str(new_trading_pair_id)) 
        RedisUtility.set_hash_field("symbol" , symbol , "1")
        RedisUtility.set_key("symbolChanged" , "1") 
        examount =float(orderDetail['result'][txid]['vol_exec'])
        PositionCRUD.create_position(
            stage=0,  # Convert to int
            trading_pair_id=new_trading_pair_id,  # Ensure it's int
            symbol=name,  # String
            buy_price=float(rebuy_price),  # Ensure float
            current_buy_price=float(currentPrice),  # Ensure float
            amount=examount,  # Ensure float
            status="Open",
            sell_price=float(take_profit_price),  # Ensure float
            pln=0.0,  # Ensure float
            raw_response=orderDetail  # Replace {} with None
        )
        return new_trading_pair

    @staticmethod
    def get_trading_pair_by_id(trading_pair_id):
        """
        Retrieve a TradingPair entry by its ID.
        """
        return TradingPair.query.get(trading_pair_id)

    @staticmethod
    def get_trading_pair_by_name(name):
        """
        Retrieve a TradingPair entry by its exact name.
        """
        return TradingPair.query.filter_by(name=name).first()


    @staticmethod
    def get_all_trading_pairs():
        """
        Retrieve all TradingPair entries.
        """
        return TradingPair.query.all()

    @staticmethod
    def update_trading_pair(trading_pair_id, **kwargs):
        """
        Update an existing TradingPair entry.
        Accepts keyword arguments for the fields to update.
        """
        trading_pair = TradingPair.query.get(trading_pair_id)
        if not trading_pair:
            return None
        
        for key, value in kwargs.items():
            if hasattr(trading_pair, key):
                setattr(trading_pair, key, value)

        db.session.commit()
        return trading_pair

    @staticmethod
    def update_trading_pair_capital(trading_pair_id, capital):
        """
        Update the current capital of an existing TradingPair entry.
        """
        pair = TradingPair.query.get(trading_pair_id)
        if not pair:
            raise Exception("Trading pair not found")

        try:
            print("Updating Trading Pair:", pair.name)
            RedisUtility.set_key(pair.name+"current_capital" ,str(capital))
            pair.current_capital = capital  # Corrected assignment
            RedisUtility.set_key(pair.name+"money" ,str(capital))
            pair.initial_capital = capital  # Corrected assignment
            db.session.commit()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating trading pair: {str(e)}")

    @staticmethod
    def update_trading_pair_money(trading_pair_id, capital , action):
        """
        Update the current capital of an existing TradingPair entry.
        """
        pair = TradingPair.query.get(trading_pair_id)
        if not pair:
            raise Exception("Trading pair not found")

        try:
            if action == "+":
                currentMoney = float(RedisUtility.get_key(pair.name+"money"))
                newCapital = capital+currentMoney
                RedisUtility.set_key(pair.name+"money" ,str(newCapital))
                pair.initial_capital = newCapital  # Corrected assignment
                db.session.commit()
                return True
            if action == "-":
                currentMoney = float(RedisUtility.get_key(pair.name+"money"))
                print(f"Current Capital = {currentMoney} and cost = {capital}")
                newCapital = currentMoney-capital
                RedisUtility.set_key(pair.name+"money" ,str(newCapital))
                pair.initial_capital = newCapital  # Corrected assignment
                db.session.commit()
                return True
            print("Updating Trading Pair:", pair.name)
            # RedisUtility.set_key(pair.name+"money" ,str(capital))
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating trading pair: {str(e)}")

    @staticmethod
    def update_trading_pair_TakeProfit(trading_pair_id, takeProfit):
        """
        Update the current capital of an existing TradingPair entry.
        """
        pair = TradingPair.query.get(trading_pair_id)
        if not pair:
            raise Exception("Trading pair not found")

        try:
            print("Updating Trading Pair:", pair.name)
            RedisUtility.set_key(pair.name+"take_profit_percentage" , takeProfit)
            # RedisUtility.set_key(pair.name+"current_capital" ,str(capital))
            pair.take_profit_percentage= takeProfit,
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating trading pair: {str(e)}")

    @staticmethod
    def update_trading_pair_ReBuy(trading_pair_id, Rebuy):
        """
        Update the current capital of an existing TradingPair entry.
        """
        pair = TradingPair.query.get(trading_pair_id)
        if not pair:
            raise Exception("Trading pair not found")

        try:
            print("Updating Trading Pair:", pair.name)
            RedisUtility.set_key(pair.name+"rebuy_percentage" , Rebuy)
            # RedisUtility.set_key(pair.name+"current_capital" ,str(capital))
            pair.rebuy_percentage= Rebuy,
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating trading pair: {str(e)}")
# tradeUsage
    @staticmethod
    def update_trading_pair_tradeUsage(trading_pair_id, tradeUsage):
        """
        Update the current capital of an existing TradingPair entry.
        """
        pair = TradingPair.query.get(trading_pair_id)
        if not pair:
            raise Exception("Trading pair not found")

        try:
            print("Updating Trading Pair:", pair.name)
            # RedisUtility.set_key(pair.name+"rebuy_percentage" , Rebuy)
            RedisUtility.set_key(pair.name+"trade_usage_percentage" , tradeUsage)
            # RedisUtility.set_key(pair.name+"current_capital" ,str(capital))
            pair.trade_usage_percentage= tradeUsage,
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating trading pair: {str(e)}")
    @staticmethod
    def delete_trading_pair(trading_pair_id):
        """
        Delete a TradingPair entry by its ID.
        Also removes all Redis keys starting with the trading pair's symbol.
        """
        trading_pair = TradingPair.query.get(trading_pair_id)
        
        if not trading_pair:
            return False  # Return False if trading pair does not exist
        
        try:
            symbol = trading_pair.name  # Get the trading pair's symbol
            
            # Delete all Redis keys starting with the symbol
            keys_to_delete = [key for key in RedisUtility._client.scan_iter(f"{symbol}*")]
            if keys_to_delete:
                RedisUtility._client.delete(*keys_to_delete)
            
            # Delete the specific symbol key from Redis
            RedisUtility._client.hdel("symbol", symbol)

            # Delete the trading pair from the database
            db.session.delete(trading_pair)
            db.session.commit()
            
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting trading pair: {e}")
            return False




# curl -X POST http://127.0.0.1:5000/bot/stage-complete      -H "Content-Type: application/json"      -d '{
#               "symbol": "AVAXUSD",
#                "hitType": "rebuy"
#              }'


# curl -X POST http://127.0.0.1:5000/bot/stage-complete      -H "Content-Type: application/json"      -d '{
# "symbol": "GALAUSD",
# "hitType": "TakeProfit"
#  }'