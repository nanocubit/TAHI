cmake_minimum_required(VERSION 3.20)
project(tahi_fastlanes_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT DEFINED FASTLANES_DIR)
  message(FATAL_ERROR "FASTLANES_DIR must point to a FastLanes checkout")
endif()

add_subdirectory("${FASTLANES_DIR}" "${CMAKE_BINARY_DIR}/fastlanes" EXCLUDE_FROM_ALL)

add_executable(tahi_fastlanes_probe main.cpp)
target_link_libraries(tahi_fastlanes_probe PRIVATE fastlanes)
target_compile_options(tahi_fastlanes_probe PRIVATE -Wall -Wextra -Wpedantic)
