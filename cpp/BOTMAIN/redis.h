#pragma once
#include <iostream>
#include <hiredis/hiredis.h>
#include <string>
#include <iostream>
#include <unordered_map>
#include <mutex>  // This is the missing include for std::once_flag and std::call_once
#include <unordered_map>
class RedisConnection {
public:
    static redisContext* get_client() {
        std::call_once(initInstanceFlag, &RedisConnection::init_client);
        return redis_client;
    }

private:
    static void init_client() {
        redis_client = redisConnect("127.0.0.1", 6379);
        if (redis_client == nullptr || redis_client->err) {
            if (redis_client) {
                std::cerr << "Redis connection error: " << redis_client->errstr << std::endl;
                redisFree(redis_client);
            } else {
                std::cerr << "Unable to allocate Redis context" << std::endl;
            }
            exit(1);
        }
        std::cout << "Connected to Redis server successfully!" << std::endl;
    }

    static redisContext* redis_client;
    static std::once_flag initInstanceFlag;
};

redisContext* RedisConnection::redis_client = nullptr;
std::once_flag RedisConnection::initInstanceFlag;

class RedisHelper {
public:
    static std::string get(const std::string& key, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }
        
        redisReply* reply = (redisReply*)redisCommand(redis_client, "GET %s", key.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return "";
        }

        std::string result = reply->type == REDIS_REPLY_STRING ? reply->str : "";
        freeReplyObject(reply);

        return result;
    }

    static bool set(const std::string& key, const std::string& value, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }
        
        redisReply* reply = (redisReply*)redisCommand(redis_client, "SET %s %s", key.c_str(), value.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return false;
        }

        bool success = (reply->type == REDIS_REPLY_STATUS && std::string(reply->str) == "OK");
        freeReplyObject(reply);
        
        return success;
    }

    static bool hset(const std::string& hash_key, const std::string& field, const std::string& value, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }
        
        redisReply* reply = (redisReply*)redisCommand(redis_client, "HSET %s %s %s", hash_key.c_str(), field.c_str(), value.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return false;
        }

        bool success = (reply->type == REDIS_REPLY_INTEGER && reply->integer == 1);
        freeReplyObject(reply);
        
        return success;
    }

    static std::string hget(const std::string& hash_key, const std::string& field, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }
    
        redisReply* reply = (redisReply*)redisCommand(redis_client, "HGET %s %s", hash_key.c_str(), field.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return "";
        }
    
        // // Debugging: print raw reply structure
        // std::cerr << "Raw Redis reply:" << std::endl;
        // std::cerr << "Type: " << reply->type << std::endl;
        // std::cerr << "Length: " << reply->len << std::endl;
    
        if (reply->type == REDIS_REPLY_STRING) {
            std::cerr << "Data: " << reply->str << std::endl;
        } else if (reply->type == REDIS_REPLY_INTEGER) {
            std::cerr << "Integer: " << reply->integer << std::endl;
        } else if (reply->type == REDIS_REPLY_ARRAY) {
            std::cerr << "Array elements: " << reply->elements << std::endl;
            for (size_t i = 0; i < reply->elements; i++) {
                std::cerr << "Element " << i << ": " << reply->element[i]->str << std::endl;
            }
        } else if (reply->type == REDIS_REPLY_STATUS) {
            std::cerr << "Status: " << reply->str << std::endl;
        } else {
            std::cerr << "Unknown reply type" << std::endl;
        }
    
        std::string result = reply->type == REDIS_REPLY_STRING ? reply->str : "";
        freeReplyObject(reply);
    
        return result;
    }
    // static std::unordered_map<std::string, std::string> hgetall(const std::string& hash_key, redisContext* redis_client = nullptr) {
    //     std::unordered_map<std::string, std::string> result;
    //     if (!redis_client) {
    //         redis_client = RedisConnection::get_client();
    //     }

    //     redisReply* reply = (redisReply*)redisCommand(redis_client, "HGETALL %s", hash_key.c_str());
    //     if (reply == nullptr) {
    //         std::cerr << "Error executing command" << std::endl;
    //         return result;
    //     }

    //     if (reply->type == REDIS_REPLY_ARRAY) {
    //         for (size_t i = 0; i < reply->elements; i += 2) {
    //             std::string field = reply->element[i]->str;
    //             std::string value = reply->element[i + 1]->str;
    //             result[field] = value;
    //         }
    //     }
    //     freeReplyObject(reply);

    //     return result;
    // }
    static bool del(const std::string& key, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }

        redisReply* reply = (redisReply*)redisCommand(redis_client, "DEL %s", key.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return false;
        }

        bool success = (reply->type == REDIS_REPLY_INTEGER && reply->integer > 0);
        freeReplyObject(reply);

        return success;
    }

    static std::unordered_map<std::string, std::string> hgetall(const std::string& hash_key, redisContext* redis_client = nullptr) {
        std::unordered_map<std::string, std::string> result;
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }

        redisReply* reply = (redisReply*)redisCommand(redis_client, "HGETALL %s", hash_key.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return result;
        }

        if (reply->type == REDIS_REPLY_ARRAY) {
            for (size_t i = 0; i < reply->elements; i += 2) {
                std::string field = reply->element[i]->str;
                std::string value = reply->element[i + 1]->str;
                result[field] = value;
            }
        }
        freeReplyObject(reply);

        return result;
    }
    static bool exists(const std::string& key, redisContext* redis_client = nullptr) {
        if (!redis_client) {
            redis_client = RedisConnection::get_client();
        }

        // Send the EXISTS command to Redis
        redisReply* reply = (redisReply*)redisCommand(redis_client, "EXISTS %s", key.c_str());
        if (reply == nullptr) {
            std::cerr << "Error executing command" << std::endl;
            return false;
        }

        // The reply type should be REDIS_REPLY_INTEGER, where 1 means the key exists and 0 means it does not
        bool keyExists = (reply->type == REDIS_REPLY_INTEGER && reply->integer == 1);
        freeReplyObject(reply);

        return keyExists;
    }
private:
    static bool check_reply(redisReply* reply) {
        return reply != nullptr && reply->type != REDIS_REPLY_ERROR;
    }
};


// curl -X POST http://127.0.0.1:2000/bot/stage-complete      -H "Content-Type: application/json"      -d '{
//    "symbol": "BTCUSD",
//            "hitType": "rebuy"
//      }'