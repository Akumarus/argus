#pragma once
#include "adc.h"

class Adc {
public:
    static constexpr uint8_t Channels = 3;
    using Callback = void (*)(uint16_t* data);

    Adc() = default;

    void Init(ADC_HandleTypeDef *hadc, Callback cb);
    void Calib();
    void Start();

    static void OnComplite();
private:
    static inline Adc* instance = nullptr;

    ADC_HandleTypeDef* adc;
    uint16_t buf[Channels];
    Callback callback;
};