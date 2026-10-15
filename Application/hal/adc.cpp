#include "adc.hpp"

void Adc::Init(ADC_HandleTypeDef *hadc, Callback cb)
{
    adc = hadc;
    callback = cb;
    instance = this;
}

void Adc::Calib()
{
    HAL_ADCEx_Calibration_Start(adc);
}

void Adc::Start()
{
    HAL_ADC_Start_DMA(adc, reinterpret_cast<uint32_t*>(buf), Channels);
}

void Adc::OnComplite()
{
    if (instance && instance->callback) {
        instance->callback(instance->buf);
    }
}

extern "C" void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
    Adc::OnComplite();
}