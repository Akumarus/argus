import canopen
from time import sleep

class CanLink:
    TX_PDO1 = 0x180
    TX_PDO2 = 0x280
    TX_PDO3 = 0x380
    TX_PDO4 = 0x480

    def __init__(self, interface, channel, bitrate):
        self.net = canopen.Network()
        self.net.connect(interface=interface, channel=channel, bitrate=bitrate)

    def subscribe_txpdo1(self, node_id):
        self.net.subscribe(self.TX_PDO1 + node_id, self._on_tpdo)

    def _on_tpdo(self, cob_id, data, timestamp):
        print(f"Cob_id: {cob_id}")
        print(f"Data: {data}")
        print(f"Len: {len(data)}")

    def close(self):
        self.net.disconnect()


interface = "slcan"
channel = "COM5"
bitrate = 500000
link = CanLink(interface, channel, bitrate)
link.subscribe_txpdo1(1)
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    link.close()
