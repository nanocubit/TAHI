cmake_minimum_required(VERSION 3.20)
project(tahi_fastlanes_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT DEFINED FASTLANES_DIR)
  message(FATAL_ERROR "FASTLANES_DIR must point to a FastLanes checkout")
endif()

add_executable(tahi_fastlanes_probe main.cpp)
target_include_directories(tahi_fastlanes_probe PRIVATE "${FASTLANES_DIR}/include")
target_compile_options(tahi_fastlanes_probe PRIVATE -Wall -Wextra -Wpedantic)
