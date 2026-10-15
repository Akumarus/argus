#include "adc.hpp"
#include "adc.h"



Adc::Adc()
{

}

void Adc::Calibrate()
{
    HAL_ADCEx_Calibration_Start(&hadc1);
}

void Adc::Start()
{
    // HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, 3);
}

void Adc::OnComplite()
{
    
}