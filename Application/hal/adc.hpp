#pragma once

class Adc {
public:
    Adc();
    ~Adc() = default;

    void Calibrate();
    void Start();
    static void OnComplite();


};