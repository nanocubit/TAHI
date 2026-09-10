#include <fastlanes.hpp>

#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    const std::vector<uint32_t> input{0, 1, 2, 3, 7, 42, 255, 1024, 65535};
    std::vector<uint32_t> encoded(input.size());
    std::vector<uint32_t> decoded(input.size());

    fastlanes::FastLanes<uint32_t> codec;
    codec.encode(input.data(), input.size(), encoded.data());
    codec.decode(encoded.data(), input.size(), decoded.data());

    assert(input == decoded);
    std::cout << "FastLanes round-trip OK\n";
    return 0;
}
