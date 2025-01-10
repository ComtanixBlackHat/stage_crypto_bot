#ifndef MARKET_DATA_SERVER_H
#define MARKET_DATA_SERVER_H

#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>
#include <set>
#include <map>
#include <string>
#include <functional>

class KrakenClient;

typedef websocketpp::server<websocketpp::config::asio> server;
typedef websocketpp::connection_hdl connection_hdl;

class MarketDataServer {
public:
    MarketDataServer();
    void run(uint16_t port);

private:
    server m_server;
    KrakenClient* m_kraken_client;

    std::set<connection_hdl, std::owner_less<connection_hdl>> m_connections;
    std::map<connection_hdl, std::string, std::owner_less<connection_hdl>> m_subscriptions;

    void on_open(connection_hdl hdl);
    void on_close(connection_hdl hdl);
    void on_message(connection_hdl hdl, server::message_ptr msg);
    void send_market_data(const std::string& market_data);
    void on_kraken_message(const std::string& data);
};

#endif // MARKET_DATA_SERVER_H
