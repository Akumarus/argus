#pragma once
#include "stdint.h"

class Can
{
public:
    Can();
    ~Can();
    void config();
    void start();

    void send(uint32_t id, uint8_t* data, uint32_t size);
};