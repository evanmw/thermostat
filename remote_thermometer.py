
import bluetooth
import time

BD_ADDR = "B8:27:EB:8B:68:DA"
PORT = 1
SAMPLE_FREQ = 60 # Hz

class BTThermometer():
    def __init__(self, BD_ADDR, PORT, SAMPLE_FREQ):
        self.connected = False
        self.bd_addr = BD_ADDR
        self.port = PORT
        self.freq = SAMPLE_FREQ
        self.sock = None

        self.bt_connect()

    def run(self):
        while (1):
            try:
                self.sock.send("68")
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