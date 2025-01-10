#ifndef WEBSOCKET_HANDLER_H
#define WEBSOCKET_HANDLER_H

#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>

class MarketDataServer;

class WebSocketHandler {
public:
    WebSocketHandler(MarketDataServer* server);
    void on_open(websocketpp::connection_hdl hdl);
    void on_close(websocketpp::connection_hdl hdl);
    void on_message(websocketpp::connection_hdl hdl, websocketpp::server<websocketpp::config::asio>::message_ptr msg);

private:
    MarketDataServer* m_server;
};

#endif // WEBSOCKET_HANDLER_H
