#include <sw/redis++/redis++.h>
#include <iostream>
#include <string>

using namespace sw::redis;

int main() {
    // Connect to Redis server
    Redis redis("tcp://127.0.0.1:6379");

    // Make sure the keys are strings, not integers or other types
    std::string key = "my_key";
    std::string value = "Hello, Redis!";

    // Set and get keys
    redis.set(key, value);
    auto val = redis.get(key);

    if (val) {
        std::cout << "Value of " << key << ": " << *val << std::endl;
    } else {
        std::cout << "Key not found!" << std::endl;
    }

    return 0;
}
