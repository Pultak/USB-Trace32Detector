#include <chrono>
#include <thread>

static constexpr int LOOP_DELAY_S = 10;

int main() {
    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(LOOP_DELAY_S * 1000));
    }
    return 0;
}
