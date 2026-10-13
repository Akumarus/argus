#pragma once
#include <stdint.h>
#include "cmsis_compiler.h"


class Critical {
public:
    Critical() 
    {
        primask = __get_PRIMASK();
        __disable_irq(); 
    }
    
    ~Critical()
    {
        __set_PRIMASK(primask);
    }

    Critical(const Critical&) = delete;
    Critical& operator=(const Critical&) = delete;
    
private:
    uint32_t primask;
};