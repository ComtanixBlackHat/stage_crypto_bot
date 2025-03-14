#include <iostream>

#include "libs/apis/database/position.h"

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <hitType> <symbol>" << std::endl;
        return 1; // Exit with error
    }

    std::string hitType = argv[1];
    std::string symbol = argv[2];

    // Call the function
    PositionApiClient::createPosition(hitType, symbol);

    return 0;
}

