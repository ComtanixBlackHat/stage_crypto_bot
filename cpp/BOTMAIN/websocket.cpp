//g++ -std=c++17 websocket.cpp -o KrakenWSClient -lboost_system -pthread -lssl -lcrypto -lhiredis -lcurl
#include <websocketpp/config/asio_client.hpp>
#include <websocketpp/client.hpp>
#include <iostream>
#include <chrono> // Include chrono library for time calculations
#include <nlohmann/json.hpp>
#include <sstream> // Include stringstream for string manipulation
#include <fstream>
#include "redis.h"
#include <unordered_map>
#include "libs/apis/database/position.h"
// Define a struct to hold OHLC data
using json = nlohmann::json;
redisContext* redis_client = RedisConnection::get_client();
struct OHLCData {
    std::string symbol;
    double open;
    double high;
    double low;
    double close;
    int trades;
    double volume;
    double vwap;
    std::string interval_begin;
    int interval;
    std::string timestamp;

    // Method to parse the JSON data into the struct
    static OHLCData from_json(const json& j) {
        OHLCData data;
        data.symbol = j["symbol"];
        data.open = j["open"];
        data.high = j["high"];
        data.low = j["low"];
        data.close = j["close"];
        data.trades = j["trades"];
        data.volume = j["volume"];
        data.vwap = j["vwap"];
        data.interval_begin = j["interval_begin"];
        data.interval = j["interval"];
        data.timestamp = j["timestamp"];
        return data;
    }
};
typedef websocketpp::client<websocketpp::config::asio_tls_client> client;
typedef websocketpp::lib::shared_ptr<websocketpp::lib::asio::ssl::context> context_ptr;
using json = nlohmann::json;
using websocketpp::lib::placeholders::_1;
using websocketpp::lib::placeholders::_2;
using websocketpp::lib::bind;

std::string getCurrentTimeInMillis() {
    auto now = std::chrono::system_clock::now();
    auto duration = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    return std::to_string(millis);
}
void close_connection(client& c, websocketpp::connection_hdl hdl) {
    websocketpp::lib::error_code ec;
    c.close(hdl, websocketpp::close::status::normal, "Closing connection", ec);
    if (ec) {
        std::cout << "Error closing WebSocket: " << ec.message() << std::endl;
    } else {
        std::cout << "WebSocket connection closed successfully!" << std::endl;
    }
}

void appendToFile(const std::string& filename, const std::string& content) {
    std::ofstream file(filename, std::ios_base::app);
    if (file.is_open()) {
        file << content;
        file.close();
    } else {
        std::cerr << "Unable to open file for appending: " << filename << std::endl;
    }
}

// void on_open(websocketpp::connection_hdl hdl, client* c) {
//     std::cout << "WebSocket connection opened!" << std::endl;
//     websocketpp::lib::error_code ec;
//     client::connection_ptr con = c->get_con_from_hdl(hdl, ec);

//     if (ec) {
//         std::cout << "Failed to get connection pointer: " << ec.message() << std::endl;
//         return;
//     }

//     // Corrected Kraken OHLC WebSocket subscription JSON
//     json subscribe_msg = {
//         for (const auto& pair : result) {
//             // std::cout << "Field: " << pair.first << " Value: " << pair.second << std::endl;
//             if (pair.second == "1") {
//                 // Use push_back instead of append for vector
//                 symbolList.push_back(pair.first);
//             }
//         }
//         i want to su to the symbols which are found in symbolList
//         {"method", "subscribe"},
//         {"params", {
//             {"channel", "ohlc"},
//             {"symbol", {"ALGO/USD", "MATIC/USD"}},  // List of symbols to subscribe to
//             {"interval", 5}  // Interval in minutes
//         }}
//     };

//     // Send the subscription message
//     c->send(con, subscribe_msg.dump(), websocketpp::frame::opcode::text);
// }
// // void on_message(websocketpp::connection_hdl, client::message_ptr msg) {

void on_open(websocketpp::connection_hdl hdl, client* c) {
    std::cout << "WebSocket connection opened!" << std::endl;
    websocketpp::lib::error_code ec;
    client::connection_ptr con = c->get_con_from_hdl(hdl, ec);

    if (ec) {
        std::cout << "Failed to get connection pointer: " << ec.message() << std::endl;
        return;
    }
    auto result = RedisHelper::hgetall("symbol", redis_client);
    // Extract symbols dynamically
    std::vector<std::string> symbolList;
    for (const auto& pair : result) {  // Assuming 'result' is a map<string, string>
        
            symbolList.push_back(pair.first);
        
    }

    // Convert symbolList to JSON array
    json symbolArray = json::array();
    for (const auto& symbol : symbolList) {
        symbolArray.push_back(symbol);
    }

    // Construct WebSocket subscription message
    json subscribe_msg = {
        {"method", "subscribe"},
        {"params", {
            {"channel", "ohlc"},
            {"symbol", symbolArray},  // Use dynamically created symbol list
            {"interval", 5}
        }}
    };

    // Send the subscription message
    c->send(con, subscribe_msg.dump(), websocketpp::frame::opcode::text);
}

void on_message(websocketpp::connection_hdl hdl, client::message_ptr msg, client* c) {
    try {
        // std::cout << msg->get_payload() << "\n";
        // RedisUtility.set_key("symbolChanged" , "1")
        std::string restartStream = RedisHelper::get("symbolChanged", redis_client);
        if (restartStream == "1") {
            std::cout << "Closing WebSocket due to symbol change." << std::endl;
            close_connection(*c, hdl);
            return;
        }
        // Retrieve all fields and values from Redis
        auto result = RedisHelper::hgetall("symbol", redis_client);

        // Use a vector (or any appropriate container) to hold the symbols
        std::vector<std::string> symbolList;

        // Loop through the result and add symbols where the value is "1"
        for (const auto& pair : result) {
            // std::cout << "Field: " << pair.first << " Value: " << pair.second << std::endl;
            if (pair.second == "1") {
                // Use push_back instead of append for vector
                symbolList.push_back(pair.first);
            }
        }

        // Parse the JSON message
        json json_decoded = json::parse(msg->get_payload());

        // Check if "type" is present and equals "update"
        if (json_decoded.contains("type") && json_decoded["type"] == "update") {
            if (json_decoded["channel"] == "ohlc") {
                auto& data = json_decoded["data"];
                // std::cout <<"\n"<< msg->get_payload() << "\n";
                // Use pointers for iterating over the data
                for (auto& candle : data) {
                    std::string symbol = candle["symbol"];
                    symbol.erase(std::remove(symbol.begin(), symbol.end(), '/'), symbol.end());
                    std::cout<<std::endl <<symbol<<std::endl; 
                    double open = candle["open"];
                    double high = candle["high"];
                    double low = candle["low"];
                    double close = candle["close"];
                    double volume = candle["volume"];
                    std::string interval_begin = candle["interval_begin"];
                    
                    std::string currentStage = symbol+"currentStage";
                    std::cout<<std::endl << currentStage<<std::endl;
                    
                    bool exists = RedisHelper::exists(currentStage);
                    std::cout<<std::endl <<exists<<std::endl;
                    
                    
                    if (exists) {
                        // std::cout << "Key exists in Redis!" << std::endl;
                        
                        std::string stage = RedisHelper::get(currentStage, redis_client);
                        std::string StageKey = symbol+stage;
                        std::string buy_pricestr = RedisHelper::get(StageKey + "buy_price", redis_client);

                        std::string sell_pricestr = RedisHelper::get(StageKey + "sell_price", redis_client);
                        float buy_price = std::stof(buy_pricestr );
                        float sell_price  = std::stof(sell_pricestr);
                        
                        
                        // std::cout<<"Current Stage = "<<currentStage<<" : "<<RedisHelper::get(currentStage, redis_client)<<std::endl;
                        // std::cout << "Buy Price: " << buy_price << std::endl;
                        // std::cout << "Symbol: " << symbol << std::endl;
                        // std::cout <<"Current Price : " <<  close<< std::endl;
                        // std::cout << "Sell Price: " << sell_price << std::endl;  


                        if(close > sell_price ) //profit
                        // std::cout << "Symbol: " << symbol << std::endl;
                        {
                            RedisHelper::hset("symbol" , symbol , "0");
                            std::cout << "Buy Price: " << buy_price << std::endl;
                            std::cout << "Symbol: " << symbol << std::endl;

                            std::cout << "Sell Price: " << sell_price << std::endl;
                            const std::string hitType = "TakeProfit";
                            std::cout << "\n\n*****************Taking Profit *************\n\n";
                            PositionApiClient::createPosition(hitType , symbol);
                            return;
                        }
                        else if(close <= buy_price)
                        {
                            RedisHelper::hset("symbol" , symbol , "0");
                            const std::string hitType = "rebuy";

                            std::cout << "\n\n*****************Rebuy  *************\n\n";
                            PositionApiClient::createPosition(hitType , symbol);
                            return;
                            // RedisHelper::hset("symbol" , symbol , "1");
                        }
                        // Output the retrieved values
                        
                        // std::cout << "Amount: " << amount << std::endl;

                    }
                    
                }
            }
        } else {
            // std::cout << "Message type is not 'update'. Skipping..." << std::endl;
        }
    } catch (const std::exception& e) {
        std::cout << "Error parsing message: " << e.what() << std::endl;
    }
}



void on_fail(websocketpp::connection_hdl hdl) {
    std::cout << "WebSocket connection failed!" << std::endl;
}

void on_close(websocketpp::connection_hdl hdl) {
    std::cout << "WebSocket connection closed!" << std::endl;
}

context_ptr on_tls_init(const char* hostname, websocketpp::connection_hdl) {
    context_ptr ctx = websocketpp::lib::make_shared<boost::asio::ssl::context>(boost::asio::ssl::context::sslv23);
    try {
        ctx->set_options(boost::asio::ssl::context::default_workarounds |
                         boost::asio::ssl::context::no_sslv2 |
                         boost::asio::ssl::context::no_sslv3 |
                         boost::asio::ssl::context::single_dh_use);
    } catch (std::exception& e) {
        std::cout << "TLS Initialization Error: " << e.what() << std::endl;
    }

    return ctx;
}

int main(int argc, char* argv[]) {
    client c;
    std::string hostname = "ws.kraken.com/v2";  // Kraken WebSocket OHLC endpoint
    std::string uri = "wss://" + hostname;
    // RedisHelper::get("symbolChanged", redis_client)
    RedisHelper::set("symbolChanged","0" ,  redis_client);
    try {
        c.set_access_channels(websocketpp::log::alevel::all);
        c.clear_access_channels(websocketpp::log::alevel::frame_payload);
        c.set_error_channels(websocketpp::log::elevel::all);
        c.init_asio();

        // c.set_message_handler(&on_message);
        c.set_message_handler(bind(&on_message, ::_1, ::_2, &c));
        c.set_tls_init_handler(bind(&on_tls_init, hostname.c_str(), ::_1));

        c.set_open_handler(bind(&on_open, ::_1, &c));
        c.set_fail_handler(bind(&on_fail, ::_1));
        c.set_close_handler(bind(&on_close, ::_1));
        c.set_error_channels(websocketpp::log::elevel::all); // Enable detailed error logging

        websocketpp::lib::error_code ec;
        client::connection_ptr con = c.get_connection(uri, ec);
        if (ec) {
            std::cout << "Could not create connection because: " << ec.message() << std::endl;
            return 0;
        }
        c.connect(con);

        c.run();
    } catch (websocketpp::exception const& e) {
        std::cout << "WebSocket Exception: " << e.what() << std::endl;
    }

    return 0;
}

