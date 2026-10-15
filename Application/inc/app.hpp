#pragma once
#include "canopen.hpp"
#include "acs712.hpp"

class App {
public:
    App() = default;
    static void Init();
    static void Run();

private:
    inline static Canopen canopen;
    inline static Acs712 acs712[3];
};