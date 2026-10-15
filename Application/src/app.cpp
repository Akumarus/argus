#include "app.hpp"
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