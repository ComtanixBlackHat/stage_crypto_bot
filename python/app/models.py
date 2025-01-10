from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # More fields can be added as needed

class TradingPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    initial_capital = db.Column(db.Float, nullable=False)
    current_capital = db.Column(db.Float, nullable=False)
    take_profit_percent = db.Column(db.Float, nullable=False)
    rebuy_percent = db.Column(db.Float, nullable=False)
    # Other trading pair related fields

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trading_pair_id = db.Column(db.Integer, db.ForeignKey('trading_pair.id'), nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    # Fields for managing position states
