import bluetooth
import time
from datetime import datetime
from thermometer import Thermometer

BD_ADDR = "B8:27:EB:8B:68:DA"
PORT = 1
SAMPLE_FREQ = 1 # Hz
THERMOMETER_BIAS_CORRECTION = -2.7 # degrees C

class BTThermometer():
    def __init__(self, bd_addr, port, sample_freq):
        self.connected = False
        self.bd_addr = bd_addr
        self.port = port
        self.freq = sample_freq
        self.sock = None

        self.thermometer = Thermometer(THERMOMETER_BIAS_CORRECTION)

        self.bt_connect()

    def run(self):
        while (1):
            try:
                cur_time = datetime.now()
                self.sock.send("%s, %f" % (cur_time.strftime('%b %d %Y %I:%M:%S%p'),
                               self.thermometer.read_temp()))
            except bluetooth.btcommon.BluetoothError as e:
                print ("Bluetooth error: %s" % e)
                self.bt_connect()
            time.sleep(1/SAMPLE_FREQ)

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
