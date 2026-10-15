#pragma once
#include "stdint.h"

class Canopen
{
public:
    Canopen();
    ~Canopen();
    void config();
    void start();

    void send(uint32_t id, uint8_t* data, uint32_t size);
    void sendTpdo1(uint16_t nodeId, uint8_t *data, uint32_t size);

private:
   
    enum  CobId : uint16_t {
        TPDO1 = 0x0180,
    };
};