#include "app.hpp"
#include "adc.hpp"
#include "main.h"

void App::Init()
{
  canopen.config();
  canopen.start();
}

void App::Run()
{
    uint8_t nodeId = 1;
    uint8_t data[8] = {0};
    // memcpy(&data[0], &current, sizeof(current));
    canopen.sendTpdo1(nodeId, data, sizeof(data));
    HAL_Delay(1000);
}

void App::OnAdcComplite(uint16_t *adc)
{
    for (uint8_t i = 0; i < JointCount; i ++) {
        joints[i].UpdateCurrent(adc[i]);
    }
}

extern "C" void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
    Adc::OnComplite();

    uint16_t rawAdc[App::JointCount];
    for (uint16_t i = 0; i < App::JointCount; i++) {
        rawAdc[i] = 0;
    }

    App::OnAdcComplite(rawAdc);
}