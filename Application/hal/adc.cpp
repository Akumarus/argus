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
    HAL_ADC_Start_IT(&hadc1);
}

void Adc::OnComplite()
{
    
}