#include "WebSocketServer.h"
#include "exchanges/KrakenClient.h"

#include <iostream>
#include <websocketpp/common/thread.hpp>
#include <thread>

MarketDataServer::MarketDataServer() {
    // Initialize the WebSocket server
    m_server.init_asio();
    m_server.set_open_handler(std::bind(&MarketDataServer::on_open, this, std::placeholders::_1));
    m_server.set_close_handler(std::bind(&MarketDataServer::on_close, this, std::placeholders::_1));
    m_server.set_message_handler(std::bind(&MarketDataServer::on_message, this, std::placeholders::_1, std::placeholders::_2));

    // Initialize KrakenClient and set the callback for receiving Kraken data
    m_kraken_client = new KrakenClient(std::bind(&MarketDataServer::on_kraken_message, this, std::placeholders::_1));
}

void MarketDataServer::run(uint16_t port) {
    // Listen on the specified port
    m_server.listen(port);
    // Start accepting connections
    m_server.start_accept();
    // Start the ASIO io_service loop
    m_server.run();
}

void MarketDataServer::on_open(connection_hdl hdl) {
    std::cout << "Client connected!" << std::endl;
    m_connections.insert(hdl);
}

void MarketDataServer::on_close(connection_hdl hdl) {
    std::cout << "Client disconnected!" << std::endl;
    m_connections.erase(hdl);
    m_subscriptions.erase(hdl);
}

void MarketDataServer::on_message(connection_hdl hdl, server::message_ptr msg) {
    std::string payload = msg->get_payload();
    std::cout << "Message received: " << payload << std::endl;

    // Parse the message to extract command, exchange, symbol, and interval
    std::istringstream iss(payload);
    std::string command, exchange, symbol, interval;
    iss >> command >> exchange >> symbol >> interval;

    if (command == "sub") {
        // Store subscription details for the client
        m_subscriptions[hdl] = symbol + " " + interval;
        std::cout << "Client subscribed to " << symbol << " with " << interval << " interval." << std::endl;

        // Send a confirmation to the client
        m_server.send(hdl, "Subscription successful!", websocketpp::frame::opcode::text);

        // Subscribe to Kraken WebSocket for OHLC data (delegated to KrakenClient)
        m_kraken_client->subscribe_to_ohlc(symbol, interval);
    } else {
        m_server.send(hdl, "Invalid command!", websocketpp::frame::opcode::text);
    }
}

void MarketDataServer::send_market_data(const std::string& market_data) {
    // Forward the received Kraken market data to all connected clients
    for (auto& client_hdl : m_connections) {
        try {
            m_server.send(client_hdl, market_data, websocketpp::frame::opcode::text);
        } catch (const websocketpp::exception& e) {
            std::cerr << "Error sending market data: " << e.what() << std::endl;
        }
    }
}

void MarketDataServer::on_kraken_message(const std::string& data) {
    std::cout << "Received Kraken data: " << data << std::endl;
    send_market_data(data);  // Forward Kraken data to all WebSocket clients
}
