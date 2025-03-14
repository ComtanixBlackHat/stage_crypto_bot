from app import bot_app


# app = bot_app()
app= bot_app()
if __name__ == "__main__":
    # Start the scheduler to monitor wallet balances and rebalance
    # start_scheduler()
    app.run(port=2000)
