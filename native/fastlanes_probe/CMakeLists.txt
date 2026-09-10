cmake_minimum_required(VERSION 3.20)
project(tahi_fastlanes_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(FASTLANES_DIR "" CACHE PATH "Path to a FastLanes checkout")
if(NOT FASTLANES_DIR)
  message(FATAL_ERROR "Set FASTLANES_DIR to a FastLanes checkout")
endif()

add_executable(tahi_fastlanes_probe main.cpp)
target_include_directories(tahi_fastlanes_probe PRIVATE "${FASTLANES_DIR}/include")
