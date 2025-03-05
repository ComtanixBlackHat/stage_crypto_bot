#ifndef KARAKIN_H
#define KARAKIN_H

#include <iostream>
#include <string>
#include <vector>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <curl/curl.h>
#include <sstream>
#include <iomanip>
#include <ctime>
#include <random>
#include "../../../includes/HTTPCLIENT.h"  // Assuming your HTTPClient class is in this header file

class Karakin {

public:
    // API Key and Secret, preferably read from environment or config files
    static const std::string apiKey;
    static const std::string apiSecret;

    // Method to place an order on Kraken
    static std::string placeOrder(const std::string& orderType,
                                  const std::string& actionType, const std::string& volume, const std::string& pair,
                                  const std::string& price, const std::string& clientOrderId) {

        // Generate a nonce (used for Kraken API authentication)
        std::string nonce = generateNonce();

        // Create the payload data
        std::string postData = "nonce=" + nonce +
                               "&ordertype=" + orderType +
                               "&type=" + actionType +
                               "&volume=" + volume +
                               "&pair=" + pair +
                               "&price=" + price +
                               "&cl_ord_id=" + clientOrderId;

        // Generate the API signature
        std::string signature = generateSignature(postData);

        // Set up headers for the HTTP request
        std::vector<std::string> headers = {
            "Content-Type: application/json",
            "Accept: application/json",
            "API-Key: " + apiKey,
            "API-Sign: " + signature
        };

        // Send the POST request to Kraken's API and return the response
        return HTTPClient::sendPOSTRequest("https://api.kraken.com/0/private/AddOrder", postData, headers);
    }

private:
    // Generate a unique nonce for the request
    static std::string generateNonce() {
        std::random_device rd;
        std::uniform_int_distribution<unsigned long long> dist(1, std::numeric_limits<unsigned long long>::max());
        return std::to_string(dist(rd));
    }

    // Generate the HMAC SHA-256 signature for Kraken API request
    static std::string generateSignature(const std::string& postData) {
        std::string apiPath = "/0/private/AddOrder";  // Kraken API endpoint for adding orders
        std::string message = apiPath + postData;
    
        unsigned char* key = reinterpret_cast<unsigned char*>(const_cast<char*>(apiSecret.c_str()));
        unsigned char* msg = reinterpret_cast<unsigned char*>(const_cast<char*>(message.c_str()));
    
        unsigned int len = SHA256_DIGEST_LENGTH;
        unsigned char hash[SHA256_DIGEST_LENGTH];
    
        // Use the new OpenSSL 3.0 API for HMAC
        const EVP_MD* evp_md = EVP_sha256();
        HMAC_CTX* hmacCtx = HMAC_CTX_new();
        HMAC_Init(hmacCtx, key, apiSecret.length(), evp_md);
        HMAC_Update(hmacCtx, msg, message.length());
        HMAC_Final(hmacCtx, hash, &len);
        HMAC_CTX_free(hmacCtx);
    
        // Convert the hash to a hexadecimal string
        std::ostringstream oss;
        for (int i = 0; i < len; ++i) {
            oss << std::setw(2) << std::setfill('0') << std::hex << (int)hash[i];
        }
        return oss.str();
    }
};

// Static members to store API key and secret
const std::string Karakin::apiKey = "Sc1rIvjDK4LaNzmQ7IfcrjlfLtRP7l2DyXuQK62gM6vTTghHQgcaL2PZ";
const std::string Karakin::apiSecret = "wsQzohrIl6SUX0sUa10uWO7iPQ+T5mc4q4YjubYXOq1jgyWnZum1Wj8nncj/WajsVXt9SUj9iBOhhduJ5Vf/jw==";

#endif // KARAKIN_H
