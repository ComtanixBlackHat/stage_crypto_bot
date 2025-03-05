
#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <string>
#include <unordered_set>

class BaseUrl {
public:
    // Enum to differentiate between real and simulated environments
    enum Environment {
        REAL,   // Real environment
        SIM     // Simulated environment
    };

    // Static inline variables for the real and simulated base URLs
    static inline const std::string REAL_BASE_URL = "https://api.tradestation.com/v3/";
    static inline const std::string SIM_BASE_URL = "https://sim-api.tradestation.com/v3/";
    static inline const std::string Think_AND_SWIM_REAL_BASE_URL = "https://api.schwabapi.com/";




};


class RedisKeys {
public:


    // Redis key names for storing position amounts and order types
    static inline const std::string LONG_AMOUNT_KEY = "LongAmount";
    static inline const std::string SHORT_AMOUNT_KEY = "ShortAmount";
    static inline const std::string TODAY_RECIVED_SYMBOL_LIST = "TODAY_RECIVED_SYMBOL_LIST";
    
    static inline const std::string ORDER_TYPE_KEY = "Type";


    static inline const std::string ENTRY_QUANTITY_KEY = "EQ";
    

    static inline const std::string ENUM_LONG = "Long";
    static inline const std::string ENUM_SHORT = "Short";


};

class SocketEnums {
public:


    // Redis key names for storing position amounts and order types
    static inline const std::string BUY_KEY = "Buy";
    static inline const std::string SELL_KEY = "Sell";





};

#endif // CONSTANTS_H


