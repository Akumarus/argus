#pragma once
#include <cstdint>

class Acs712 {
public:
    Acs712() : gain(V_A), offset(0.0f) {}
    ~Acs712() {}

    void calibrate(uint16_t adc) { this->offset = getVoltage(adc); }
    float calculate(uint16_t adc) { return getCurrent(adc); }

private:
    static constexpr float VREF = 3.3f;
    static constexpr float ADC_MAX = 4095.0f;
    static constexpr float DIV_K = (2.0f / 3.0f);   // делитель 10k/20k
    static constexpr float V_A = 0.185f;            // В/А для

    float gain;
    float offset;
    float current;

    constexpr float getVoltage(uint16_t adc) {
        return (adc * VREF) / ADC_MAX / DIV_K;
    }

    float getCurrent(uint16_t adc) {
        current = (getVoltage(adc) - offset) / gain;
        return current;
    }
};