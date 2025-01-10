#ifndef KRAKENCLIENT_H
#define KRAKENCLIENT_H

#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_tls_client.hpp>
#include <websocketpp/connection.hpp>
#include <iostream>
#include <json/json.h>

class KrakenClient {
public:
    typedef websocketpp::client<websocketpp::config::asio_tls_client> client;
    client m_client;

    KrakenClient();
    void connect(const std::string& uri);
    void on_message(websocketpp::connection_hdl hdl, client::message_ptr msg);
    void subscribe_ohlc(const std::vector<std::string>& symbols, int interval = 1, bool snapshot = true);
    void unsubscribe_ohlc(const std::vector<std::string>& symbols, int interval = 1);
    void send_message(const std::string& message);

private:
    websocketpp::connection_hdl m_connection;
};

#endif // KRAKENCLIENT_H
