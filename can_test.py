import can
import time

bus = can.Bus(interface='slcan', channel='COM5', bitrate=500000)

while True:
    bus.send(can.Message(arbitration_id=0x123,
                         data=[0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11],
                         is_extended_id=False))
    print("sent")
    time.sleep(0.1)