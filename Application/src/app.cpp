#include "app.hpp"
#include "adc.hpp"
#include "main.h"
#include <cstring>

void App::Init()
{
    adc.Init(&hadc1, &OnAdcComplite);
    adc.Calib();
    adc.Start();
    HAL_Delay(10);
    JointsCalibCurrent();

    canopen.config();
    canopen.start();
}

void App::Run()
{
    uint8_t nodeId = 1;
    uint8_t data[8] = {0};
    memcpy(&data[0], &joints->mA, sizeof(joints->mA));
    memcpy(&data[2], &joints->mA, sizeof(joints->mA));
    memcpy(&data[4], &joints->mA, sizeof(joints->mA));
    canopen.sendTpdo1(nodeId, data, sizeof(data));
    HAL_Delay(1000);
}

void App::JointsCalibCurrent()
{
    for(auto& joint : joints) {
        joint.CalibCurrent();
    }
}

void App::OnAdcComplite(uint16_t *adc)
{
    for (uint8_t i = 0; i < JointCount; i ++) {
        joints[i].UpdateCurrent(adc[i]);
    }
}