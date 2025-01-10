cmake_minimum_required(VERSION 3.10)
project(KrakenMarketDataServer)

# Set the C++ standard to C++14 or later
set(CMAKE_CXX_STANDARD 14)

# Find WebSocket++ and its dependencies
find_package(WebSocketPP REQUIRED)

# Add all source files, including those from the 'exchanges' folder
set(SOURCES
    main.cpp
    MarketDataFetcher.cpp
    WebSocketServer.cpp
    WebSocketHandler.cpp
    SubscriberManager.cpp
    exchanges/KrakenClient.cpp   # Reference KrakenClient.cpp in the exchanges folder
   
)

# Add all header files, including those from the 'exchanges' folder
set(HEADERS
    MarketDataFetcher.h
    WebSocketServer.h
    WebSocketHandler.h
    SubscriberManager.h
    exchanges/KrakenClient.h    # Reference KrakenClient.h in the exchanges folder
    
)

# Include the necessary directories
include_directories(
    ${CMAKE_SOURCE_DIR}        # Include the source directory for headers
    ${WebSocketPP_INCLUDE_DIR} # Include the WebSocket++ directory (installed or locally)
    ${CMAKE_SOURCE_DIR}/exchanges  # Include the 'exchanges' directory for KrakenClient headers
)

# Create an executable
add_executable(KrakenMarketDataServer ${SOURCES} ${HEADERS})

# Link against the WebSocket++ library (if using a custom installation, you may need to link manually)
target_link_libraries(KrakenMarketDataServer PRIVATE ${WebSocketPP_LIBRARIES})
