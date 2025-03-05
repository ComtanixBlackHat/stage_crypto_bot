from datetime import datetime
from app import db
from app.models import Position , OldPosition
from app.controllers.redisutil import RedisUtility
import json
class PositionCRUD:


    @staticmethod
    def create_position(
        stage: int, 
        trading_pair_id: int, 
        symbol: str,
        buy_price: float, 
        current_buy_price: float,  # New field added
        amount: float, 
        status: str = "Open", 
        sell_price: float = None, 
        pln: float = None, 
        raw_response: float = None
    ):
        # Ensure correct types
        stage = int(stage)
        trading_pair_id = int(trading_pair_id)
        buy_price = float(buy_price)
        current_buy_price = float(current_buy_price)
        amount = float(amount)
        
        if sell_price is not None:
            sell_price = float(sell_price)
        if pln is not None:
            pln = float(pln)
        if raw_response is not None and not isinstance(raw_response, (int, float)):
            raw_response = None  # Ensure it's not a dict     
        position = Position(
            stage=stage,
            trading_pair_id=trading_pair_id,
            buy_price=buy_price,
            current_buy_price=current_buy_price,  # Saving new field
            sell_price=sell_price,
            amount=amount,
            pln=pln,
            raw_response=json.dumps(raw_response) if raw_response else None,  # Convert dict to JSON string
            status=status
        )
        print("test2")
        # Store position data in Redis
        StageKey = f"{symbol}{stage}"
        RedisUtility.set_key(f"{StageKey}currentStage", str(stage))
        RedisUtility.set_key(f"{StageKey}symbol", symbol)
        RedisUtility.set_key(f"{StageKey}trading_pair_id", str(trading_pair_id))
        RedisUtility.set_key(f"{StageKey}buy_price", str(buy_price))
        RedisUtility.set_key(f"{StageKey}current_buy_price", str(current_buy_price))  # New Redis entry
        RedisUtility.set_key(f"{StageKey}sell_price", str(sell_price))
        RedisUtility.set_key(f"{StageKey}amount", str(amount))
        
        # RedisUtility.set_add(f"{StageKey}pln", pln if pln is not None else "None")
        # RedisUtility.set_add(f"{StageKey}raw_response",  json.dumps(raw_response) if raw_response is not None else None)
        RedisUtility.set_key(f"{StageKey}status", status)
        print(amount)
        print(type(amount))
        db.session.add(position)
        db.session.commit()
        
        RedisUtility.set_key(f"{StageKey}currentStageId", str(position.id))
        return position
    
    
    @staticmethod
    def create_old_position(
        stage: int, 
        trading_pair_id: int, 

    ):
        # Ensure correct types

        Oldposition = Position.query.filter_by(trading_pair_id=trading_pair_id, stage=stage).first()
        
        position = OldPosition(
            stage=stage,
            trading_pair_id=trading_pair_id,
            buy_price=Oldposition.buy_price,
            current_buy_price=Oldposition.current_buy_price,  # Saving new field
            sell_price=Oldposition.sell_price,
            amount=Oldposition.amount,
            pln=Oldposition.pln,
            raw_response=Oldposition.raw_response , # Convert dict to JSON string
            status="Closed",
            start_at = Oldposition.created_at
        )
        print("test2")

        # print(type(amount))
        db.session.add(position)
        db.session.commit()
        
        return position
    
    
    @staticmethod
    def get_position_by_id(position_id, stage):
        return Position.query.filter_by(id=position_id, stage=stage).first()

    @staticmethod
    def get_all_positions():
        return Position.query.all()

    @staticmethod
    def update_position(position_id, stage, **kwargs):
        position = Position.query.filter_by(id=position_id, stage=stage).first()
        if position:
            for key, value in kwargs.items():
                if hasattr(position, key):
                    setattr(position, key, value)
            db.session.commit()
            return position
        return None


    @staticmethod
    def get_position_by_symbol_and_stage(symbol, stage):
        # Retrieve trading_pair_id from Redis
        trading_pair_id = RedisUtility.get(f"{symbol}trading_pair_id")
        
        if not trading_pair_id:
            return None  # No position found in Redis

        # Query the database for the position
        position = Position.query.filter_by(trading_pair_id=trading_pair_id, stage=stage).first()
        return position
    
    @staticmethod
    def delete_position(position_id, stage):
        position = Position.query.filter_by(id=position_id, stage=stage).first()
        if position:
            db.session.delete(position)
            db.session.commit()
            return True
        return False
    

    @staticmethod
    def delatePos(trading_pair_id , stage):
        positions = Position.query.filter_by(trading_pair_id=trading_pair_id, stage=stage).all()

        for position in positions:
            db.session.delete(position)

        db.session.commit()

    @staticmethod
    def update_position_by_symbol_and_stage(symbol, stage, **kwargs):
        # Retrieve trading_pair_id from Redis
        # RedisUtility.set_key( , str(new_trading_pair_id)) 
        trading_pair_id = RedisUtility.get_key(symbol+"trading_pair_id")
        
        if not trading_pair_id:
            return None  # No position found in Redis
        
        # Query the database for the position
        position = Position.query.filter_by(trading_pair_id=trading_pair_id, stage=stage).first()
        
        if position:
            # Update position fields dynamically
            for key, value in kwargs.items():
                if hasattr(position, key):
                    setattr(position, key, value)

            # Commit changes to the database
            db.session.commit()

            # Update Redis if necessary
            # for key, value in kwargs.items():
            #     RedisUtility.set_add(f"{symbol}{stage}{key}", str(value))

            return position
        
        return None  # No position found in the database





# COMPUSD

# curl -X POST http://127.0.0.1:5000/bot/stage-complete      -H "Content-Type: application/json"      -d '{
#            "symbol": "SOLUSD",
#            "hitType": "rebuy"
#          }'