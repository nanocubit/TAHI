#include <fastlanes.hpp>

#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    const std::vector<uint32_t> input{0, 1, 2, 3, 7, 42, 255, 1024, 65535};
    std::vector<uint32_t> decoded(input.size());

    fastlanes::encode(input.data(), decoded.data(), input.size());
    fastlanes::decode(decoded.data(), decoded.data(), input.size());

    assert(input == decoded);
    std::cout << "FastLanes round-trip OK\n";
    return 0;
}
