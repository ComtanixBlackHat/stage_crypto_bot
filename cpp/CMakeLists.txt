cmake_minimum_required(VERSION 3.10)
project(market_data_server)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)

# Find Boost libraries (ensure Boost is installed)
find_package(Boost REQUIRED COMPONENTS system)
include_directories(${Boost_INCLUDE_DIRS})

# Add your source files
add_executable(market_data_server main.cpp)

# Link Boost.Asio library
target_link_libraries(market_data_server ${Boost_LIBRARIES})
