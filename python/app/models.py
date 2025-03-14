from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    


    def __repr__(self):
        return f"<User {self.username}>"

class TradingPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    initial_capital = db.Column(db.Float, nullable=False)
    current_capital = db.Column(db.Float, nullable=False, default=0)
    start_capital = db.Column(db.Integer, nullable=False)
    currentStage = db.Column(db.Integer, nullable=False)

    take_profit_percentage = db.Column(db.Float, nullable=False)
    rebuy_percentage = db.Column(db.Float, nullable=False)
    trade_usage_percentage = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    
    # positions = db.relationship('Position', backref='trading_pair', lazy=True)

    def __repr__(self):
        return f"<TradingPair {self.name}>"

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stage = db.Column(db.Integer, nullable=False)
    trading_pair_id = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    current_buy_price = db.Column(db.Float, nullable=False)  # New field added
    sell_price = db.Column(db.Float, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    pln = db.Column(db.Float, nullable=True)
    raw_response = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Open")

    def __repr__(self):
        return f"<Position {self.trading_pair_id} - {self.status}>"


class OldPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stage = db.Column(db.Integer, nullable=False)
    trading_pair_id = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    current_buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    pln = db.Column(db.Float, nullable=True)
    raw_response = db.Column(db.Float, nullable=True)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Closed")  # Default to 'Closed'

    def __repr__(self):
        return f"<OldPosition {self.trading_pair_id} - {self.status}>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # Buy or Sell
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.type} - {self.amount} at {self.price}>"
