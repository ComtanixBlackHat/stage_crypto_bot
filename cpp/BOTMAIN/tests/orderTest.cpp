#include <iostream>
#include "../libs/apis/exchanges/karakin.h"  // Include the Karakin class

int main() {
    // Define the order parameters for a market order
    std::string orderType = "market";  // Order type: "market" for market orders
    std::string actionType = "buy";    // Action type: "buy" or "sell"
    std::string volume = "0.1";        // Volume of the order
    std::string pair = "SOLUSD";       // Currency pair (e.g., Bitcoin to USD)
    std::string price = "";            // No price is needed for market orders
    std::string clientOrderId = "order123";  // Optional client order ID

    // Place the market order using the Karakin class
    std::string response = Karakin::placeOrder(orderType, actionType, volume, pair, price, clientOrderId);

    // Output the response from Kraken's API
    std::cout << "Kraken API Response: " << response << std::endl;

    return 0;
}

