from app import create_app


app = create_app()

if __name__ == "__main__":
    # Start the scheduler to monitor wallet balances and rebalance
    # start_scheduler()
    app.run(host="0.0.0.0")
