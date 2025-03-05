#include <websocketpp/config/asio_no_tls_client.hpp>
#include <websocketpp/client.hpp>
#include <iostream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using websocketpp::connection_hdl;
typedef websocketpp::client<websocketpp::config::asio_client> client;

class WebSocketClient {
public:
    WebSocketClient() {
        ws_client.init_asio();
        ws_client.set_open_handler(bind(&WebSocketClient::on_open, this, std::placeholders::_1));
        ws_client.set_message_handler(bind(&WebSocketClient::on_message, this, std::placeholders::_1, std::placeholders::_2));
    }

    void connect(const std::string& uri) {
        websocketpp::lib::error_code ec;
        client::connection_ptr con = ws_client.get_connection(uri, ec);
        
        if (ec) {
            std::cerr << "Connection error: " << ec.message() << std::endl;
            return;
        }
        
        ws_client.connect(con);
        ws_client.run();
    }

private:
    client ws_client;

    void on_open(connection_hdl hdl) {
        json auth_message = {
            {"token", "your_auth_token"},
            {"accountType", "your_account_type"}
        };
        ws_client.send(hdl, auth_message.dump(), websocketpp::frame::opcode::text);
        std::cout << "Sent authentication message" << std::endl;
    }

    void on_message(connection_hdl hdl, client::message_ptr msg) {
        std::cout << "Received: " << msg->get_payload() << std::endl;
        
        json sub_message = {
            {"symbol", "BTCUSDT"},
            {"interval", 5},
            {"unit", "minutes"},
            {"barsback", 50},
            {"chartType", "candlestick"},
            {"type", "subscribe"},
            {"socketid", "your_unique_socket_id"}
        };
        ws_client.send(hdl, sub_message.dump(), websocketpp::frame::opcode::text);
        std::cout << "Sent subscription message" << std::endl;
    }
};

int main() {
    WebSocketClient client;
    client.connect("ws://localhost:9001");
    return 0;
}
