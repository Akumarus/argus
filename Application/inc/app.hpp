#pragma once
#include "canopen.hpp"
#include "acs712.hpp"
#include "avg.hpp"
#include "adc.hpp"

enum class JointId : uint8_t { Coxa, Femur, Tibia, Count };

struct Joint
{
public:
    static constexpr uint16_t Samples = 100; 

    Avg<Samples> avg = {};
    Acs712 acs712 = {};
    float current = 0.0f;
    uint16_t adcAvrg = 0;
    uint16_t mA = 0;

    void UpdateCurrent(uint16_t adc)
    {
        adcAvrg = avg.update(adc);
        current = acs712.calculate(adcAvrg);
        mA = static_cast<uint16_t>(current * 1000);
    }

    void CalibCurrent()
    {
        acs712.calibrate(adcAvrg);
    }
};

class App {
public:
    static constexpr uint8_t JointCount = static_cast<uint8_t>(JointId::Count);

    App() = delete;
    static void Init();
    static void Run();

    static void JointsCalibCurrent();
    static void OnAdcComplite(uint16_t *adc);

    static Joint& getJoint(JointId id)
    {
        return joints[static_cast<uint8_t>(id)];
    }

    
private:
    inline static Joint joints[JointCount];
    inline static Canopen canopen;
    inline static Adc adc;
};

