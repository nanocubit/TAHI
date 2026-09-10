#include <iostream>

#if __has_include("fastlanes.h")
#include "fastlanes.h"
#else
#error "FastLanes include/fastlanes.h was not found"
#endif

int main() {
    std::cout << "FastLanes headers detected" << std::endl;
    return 0;
}
