#ifndef POSITION_API_CLIENT_H
#define POSITION_API_CLIENT_H

#include <string>
#include <vector>
#include <map>
#include "../../../includes/HTTPCLIENT.h"   // Assume this is a wrapper for HTTP requests

// #include "Constants.h"    // Contains the API base URL
#include <nlohmann/json.hpp>

using json = nlohmann::json;
struct PositionApiClient {
    PositionApiClient() = delete;  // Prevent instantiation

    // Create a new position
    static void createPosition(std::string hitType, const std::string& symbol) {
        json requestData = {
            {"hitType", hitType},
            {"symbol", symbol}
        };

        std::string url ="http://127.0.0.1:2000/bot/stage-complete";
        HTTPClient::sendPOSTRequest(url, requestData.dump());
        // return   // Convert JSON to string
    }

};

#endif // POSITION_API_CLIENT_H
