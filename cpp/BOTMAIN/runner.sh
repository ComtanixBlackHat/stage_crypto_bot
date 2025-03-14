#!/bin/bash

LOG_FILE="kraken_client.log"

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting KrakenWSClient..." | tee -a "$LOG_FILE"
    ./KrakenWSClient >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] KrakenWSClient crashed. Restarting in 1 second..." | tee -a "$LOG_FILE"
    sleep 1
done
