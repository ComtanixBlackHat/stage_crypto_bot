# bot_routes.py
import logging
from flask import Blueprint, request, jsonify , current_app
from app.exchanges.kerkaren.kraken import Kraken
from app.controllers.redisutil import RedisUtility
from app.controllers.crud.positionCrud import PositionCRUD
from app.controllers.crud.tradingpair import TradingPairCrud
import time
import threading
from app.controllers.bot_control import BOT_CONTROLLER
# from app.controllers
botRoutes = Blueprint('botRoutes', __name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("OrderLogs"),  # Log to a file named 'bot.log'
        logging.StreamHandler()  # Also print logs to the console (optional)
    ]
)
@botRoutes.route('/stage-complete', methods=['POST'])
def stagecomplete():
    try:
        logging.info("Received request at /stage-complete")
        
        # ✅ Get data once and pass it explicitly
        data = request.get_json()
        logging.debug(f"***************************\nRequest Data: {data}\n\n")

        # ✅ Start background thread with app context
        thread = threading.Thread(target=process_stage, args=(current_app._get_current_object(), data))
        thread.daemon = True
        thread.start()

        # ✅ Return a response immediately
        return jsonify({"status": "processing"}), 200  

    except Exception as e:
        logging.error(f"Error in stagecomplete: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Background processing function
def process_stage(app, data):
    with app.app_context():  # Ensure Flask app context
        try:
            logging.info(f"Processing data in background: {data}")
            
            # ✅ Pass `data` explicitly to BOT_CONTROLLER.process()
            BOT_CONTROLLER.process(data)

            logging.info("Task Completed!")
        except Exception as e:
            logging.error(f"Error in background process: {str(e)}")
