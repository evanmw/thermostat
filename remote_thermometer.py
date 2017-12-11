
import bluetooth
import time
from datetime import datetime

BD_ADDR = "E4:A7:A0:5A:54:28"
PORT = 1
SAMPLE_FREQ = 60 # Hz

class BTThermometer():
    def __init__(self, bd_addr, port, sample_freq):
        self.connected = False
        self.bd_addr = bd_addr
        self.port = port
        self.freq = sample_freq
        self.sock = None

        self.bt_connect()

    def run(self):
        while (1):
            try:
                time = datetime.now()
                self.sock.send("%s, 68" % datetime.strftime('%b %d %Y %I:%M%p'))
            except bluetooth.btcommon.BluetoothError as e:
                print ("Bluetooth error: %s" % e)
                self.bt_connect()
            time.sleep(60/SAMPLE_FREQ)

    def bt_connect(self):
        try:
            self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.connect((self.bd_addr, self.port))
            self.connected = True
        except bluetooth.btcommon.BluetoothError as e:
            print ("Bluetooth error: %s" % e)
            time.sleep(2)
            connected = False
            self.bt_connect()

if __name__ == '__main__':
    therm = BTThermometer(BD_ADDR, PORT, SAMPLE_FREQ)
    therm.run()
    sock.close()