#include <fastlanes.hpp>

#include <filesystem>
#include <fstream>
#include <iostream>

int main() {
    namespace fs = std::filesystem;
    const fs::path input_dir = "fastlanes_probe_input";
    const fs::path fls_path = "fastlanes_probe.fls";
    const fs::path output_csv = "fastlanes_probe_output.csv";

    fs::create_directories(input_dir);
    std::ofstream csv(input_dir / "data.csv");
    csv << "id,value\n1,10\n2,20\n3,30\n";
    csv.close();

    fastlanes::Connection connection;
    connection.reset().read_csv(input_dir).to_fls(fls_path);

    fastlanes::Connection reader;
    reader.reset().read_fls(fls_path).to_csv(output_csv);

    std::ifstream result(output_csv);
    if (!result.good()) {
        std::cerr << "FastLanes did not produce output CSV\n";
        return 1;
    }

    std::cout << "FastLanes CSV/FLS round-trip OK\n";
    return 0;
}
