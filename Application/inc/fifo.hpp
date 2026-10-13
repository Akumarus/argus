#pragma once
#include <stdint.h>
#include <stdbool.h>

template<typename T, uint32_t Size>
class Fifo {
public:
    Fifo() : buffer{}, head(0), tail(0), count(0) {}
    ~Fifo();

    bool push(const T &data)
    {
        if (isFull())
            return false;

        Critical cs; // Вход в критическую секцию
        
        buffer[tail] = data;
        tail = (tail + 1) % Size;
        count++;
        return true;
    }

    bool pop(T& data)
    {
        Critical cs; // Вход в критическую секцию

        if (isEmpty())
            return false;

        data = buffer[head];
        head = (head + 1) % Size;
        count--;
        return true;
    }

    inline bool isFull() const { return count == Size; }
    inline bool isEmpty() const { return count == 0; }
    inline uint32_t size() const { return count; }

private:
    T buffer[Size];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
};