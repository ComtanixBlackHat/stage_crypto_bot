#include "KrakenClient.h"
#include <websocketpp/lib/json.hpp>

KrakenClient::KrakenClient() {
    // Set the message handler for the client
    m_client.set_message_handler(websocketpp::lib::bind(
        &KrakenClient::on_message, this, websocketpp::lib::placeholders::_1, websocketpp::lib::placeholders::_2));
}

void KrakenClient::connect(const std::string& uri) {
    try {
        // Connect to WebSocket server
        websocketpp::uri uri_obj(uri);
        m_connection = m_client.get_connection(uri_obj.str(), nullptr);
        m_client.connect(m_connection);

        // Run the client in a separate thread
        m_client.run();
    } catch (const websocketpp::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

void KrakenClient::on_message(websocketpp::connection_hdl hdl, client::message_ptr msg) {
    try {
        // Parse incoming JSON message
        std::string payload = msg->get_payload();
        Json::Value root;
        Json::CharReaderBuilder builder;
        std::string errs;

        if (Json::parseFromStream(builder, payload, &root, &errs)) {
            if (root.isMember("channel") && root["channel"].asString() == "ohlc") {
                if (root.isMember("data")) {
                    const Json::Value& data = root["data"];
                    for (const auto& candle : data) {
                        std::cout << "Symbol: " << candle["symbol"].asString() << std::endl;
                        std::cout << "Open: " << candle["open"].asFloat() << std::endl;
                        std::cout << "High: " << candle["high"].asFloat() << std::endl;
                        std::cout << "Low: " << candle["low"].asFloat() << std::endl;
                        std::cout << "Close: " << candle["close"].asFloat() << std::endl;
                        std::cout << "Volume: " << candle["volume"].asFloat() << std::endl;
                    }
                }
            }
        } else {
            std::cerr << "Error parsing message: " << errs << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error processing message: " << e.what() << std::endl;
    }
}

void KrakenClient::subscribe_ohlc(const std::vector<std::string>& symbols, int interval, bool snapshot) {
    Json::Value root;
    root["method"] = "subscribe";
    root["params"]["channel"] = "ohlc";
    root["params"]["symbol"] = Json::Value(Json::arrayValue);

    for (const auto& symbol : symbols) {
        root["params"]["symbol"].append(symbol);
    }

    root["params"]["interval"] = interval;
    root["params"]["snapshot"] = snapshot;

    Json::StreamWriterBuilder writer;
    std::string message = Json::writeString(writer, root);
    send_message(message);
}

void KrakenClient::unsubscribe_ohlc(const std::vector<std::string>& symbols, int interval) {
    Json::Value root;
    root["method"] = "unsubscribe";
    root["params"]["channel"] = "ohlc";
    root["params"]["symbol"] = Json::Value(Json::arrayValue);

    for (const auto& symbol : symbols) {
        root["params"]["symbol"].append(symbol);
    }

    root["params"]["interval"] = interval;

    Json::StreamWriterBuilder writer;
    std::string message = Json::writeString(writer, root);
    send_message(message);
}

void KrakenClient::send_message(const std::string& message) {
    try {
        m_client.send(m_connection, message, websocketpp::frame::opcode::text);
    } catch (const websocketpp::exception& e) {
        std::cerr << "Error sending message: " << e.what() << std::endl;
    }
}
