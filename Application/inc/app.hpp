#pragma once
#include "canopen.hpp"
#include "acs712.hpp"
#include "avg.hpp"

enum class JointId : uint8_t { Coxa, Femur, Tibia, Count };

struct Joint
{
public:
    static constexpr uint16_t Samples = 100; 

    Avg<Samples> avg = {};
    Acs712 acs712 = {};
    float current = 0.0f;

    void UpdateCurrent(uint16_t adc)
    {
        current = acs712.calculate(avg.update(adc));
    }
};

class App {
public:
    static constexpr uint8_t JointCount = static_cast<uint8_t>(JointId::Count);

    App() = delete;
    static void Init();
    static void Run();
    static void OnAdcComplite(uint16_t *adc);

    static Joint& getJoint(JointId id)
    {
        return joints[static_cast<uint8_t>(id)];
    }

    
private:
    inline static Joint joints[JointCount];
    inline static Canopen canopen;
};

