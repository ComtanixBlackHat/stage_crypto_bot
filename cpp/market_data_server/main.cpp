#include "WebSocketServer.h"

int main() {
    try {
        MarketDataServer server;
        std::cout << "Starting WebSocket server on port 9002..." << std::endl;
        server.run(9002);
    } catch (const std::exception& e) {
        std::cerr << "Server error: " << e.what() << std::endl;
    }
    return 0;
}
