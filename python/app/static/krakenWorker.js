// Kraken WebSocket client implemented in a Web Worker
self.onmessage = function(event) {
    if (event.data === "start") {
        startWebSocket();
    }
};

function startWebSocket() {
    const socket = new WebSocket("wss://ws.kraken.com/v2");

    socket.onopen = function() {
        console.log("WebSocket connection opened!");
        subscribeToSymbols(socket);
    };

    socket.onmessage = function(event) {
        handleWebSocketMessage(event.data, socket);
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
    };

    socket.onclose = function() {
        console.log("WebSocket connection closed!");
    };
}

function subscribeToSymbols(socket) {
    const symbolList = ["ALGO/USD", "MATIC/USD"];
    const subscribeMsg = {
        method: "subscribe",
        params: {
            channel: "ohlc",
            symbol: symbolList,
            interval: 5
        }
    };
    socket.send(JSON.stringify(subscribeMsg));
}

function handleWebSocketMessage(data, socket) {
    try {
        const jsonDecoded = JSON.parse(data);
        if (jsonDecoded.type === "update" && jsonDecoded.channel === "ohlc") {
            jsonDecoded.data.forEach(candle => {
                const { symbol, close } = candle;
                console.log(`Symbol: ${symbol}, Close Price: ${close}`);
                checkTradeConditions(symbol, close);
            });
        }
    } catch (error) {
        console.error("Error parsing message:", error);
    }
}

function checkTradeConditions(symbol, close) {
    const buyPrice = 1.0;
    const sellPrice = 1.2;
    
    if (close >= buyPrice) {
        console.log(`TakeProfit triggered for ${symbol}`);
        postMessage({ action: "TakeProfit", symbol });
    } else if (close <= sellPrice) {
        console.log(`Rebuy triggered for ${symbol}`);
        postMessage({ action: "Rebuy", symbol });
    }
}
