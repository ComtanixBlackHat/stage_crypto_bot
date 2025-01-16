from datetime import datetime
from app import db
from app.models import TradingPair
class TradingPairCrud:
    @staticmethod
    def create_trading_pair(name, initial_capital, current_capital, current_stage, 
                            take_profit_percentage, rebuy_percentage, trade_usage_percentage, 
                            status="Active", user_id=None):
        """
        Create a new TradingPair entry.
        """
        new_trading_pair = TradingPair(
            name=name,
            initial_capital=initial_capital,
            current_capital=current_capital,
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
    def delete_trading_pair(trading_pair_id):
        """
        Delete a TradingPair entry by its ID.
        """
        trading_pair = TradingPair.query.get(trading_pair_id)
        if trading_pair:
            db.session.delete(trading_pair)
            db.session.commit()
            return True
        return False
