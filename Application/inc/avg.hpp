#pragma once
#include <cstdint>

template<uint16_t N>
class Avg {
public:
    uint16_t update(uint16_t sample)
    {
        if (n < N) {
            n++;
        } else {
            sum -= buf[idx];
        }
        sum += sample;
        buf[idx] = sample;
        idx = (idx + 1) % N;
        return sum / n;
    }

    void reset() { sum = 0; n = 0; idx = 0; }

private:
    uint16_t buf[N] = {0};
    uint32_t sum = 0;
    uint16_t idx = 0;
    uint16_t n = 0;
};