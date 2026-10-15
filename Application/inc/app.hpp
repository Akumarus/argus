#pragma once
#include "can.hpp"
#include "acs712.hpp"

class App {
public:
    App() = default;
    static void Init();
    static void Run();

private:
    static Can can;
    static Acs712 acs712[3];
};