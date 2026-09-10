#include <fastlanes.h>

#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    const std::vector<uint32_t> input{0, 1, 2, 3, 7, 42, 255, 1024, 65535};
    std::vector<uint32_t> compressed(input.size());
    std::vector<uint32_t> decoded(input.size());

    const auto compressed_size = fastlanes_compress_u32(
        input.data(), input.size(), compressed.data());
    const auto decoded_size = fastlanes_decompress_u32(
        compressed.data(), compressed_size, decoded.data(), decoded.size());

    assert(decoded_size == input.size());
    assert(input == decoded);
    std::cout << "FastLanes C API round-trip OK\n";
    return 0;
}
