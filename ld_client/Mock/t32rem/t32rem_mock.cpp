// t32rem.exe localhost port=20000 VERSION.HARDWARE
#include <chrono>
#include <thread>
#include <random>
#include <fstream>
#include <iostream>
#include <cstring>

static constexpr int EXPECTED_NUMBER_OF_ARGUMENTS = 4;
static constexpr const char *OUTPUT_FILE_NAME = "output.txt";
static constexpr const char *DEBUGGER_INFO =
        "B::version.hardware\n"
        "PowerDebug USB 3.0 via USB 3.0\n"
        "   Serial Number: C21070308132\n"
        "   Firmware R.2021.02 (136263)\n"
        "   Instance: 1.\n"
        "   Automotive Debug Cable\n"
        "      Serial Number: C17040231820\n";

static constexpr int MIN_SEC_DELAY = 1;
static constexpr int MAX_SEC_DELAY = 10;

int main(int argc, char *argv[]) {
    if (argc != EXPECTED_NUMBER_OF_ARGUMENTS) {
        std::cout << "Invalid number of arguments\n";
        std::cout << "The mock is meant to be called with the following arguments: localhost port=20000 VERSION.HARDWARE\n";
        return 1;
    }
    if (strcmp(argv[1], "localhost") != 0) {
        std::cout << "Invalid first argument (expected 'localhost')\n";
        return 2;
    }
    if (strcmp(argv[2], "port=20000") != 0) {
        std::cout << "Invalid second argument (expected 'port=20000')\n";
        return 2;
    }
    if (strcmp(argv[3], "VERSION.HARDWARE") != 0) {
        std::cout << "Invalid third argument (expected 'VERSION.HARDWARE')\n";
        return 2;
    }

    std::random_device rd;
    std::mt19937 mt(rd());
    std::uniform_int_distribution<uint32_t> distribution(MIN_SEC_DELAY, MAX_SEC_DELAY);
    uint32_t delay_s = distribution(mt);
    std::this_thread::sleep_for(std::chrono::milliseconds(delay_s * 1000));

    std::ofstream file(OUTPUT_FILE_NAME);
    if (!file) {
        std::cout << "Fail to open the output file\n";
        return 3;
    }
    file << DEBUGGER_INFO;
    file.close();

    return 0;
}
