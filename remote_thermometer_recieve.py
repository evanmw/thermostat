import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

PORT = 1

class BTThermometerServer():
    def __init__(self, port):
        self.connected = False
        self.port = PORT
        self.sock = None

        self.bt_connect()

    def run(self):
        while (1):
            data = ""
            data_valid = False
            try:
                data = client_sock.recv(1024)
                data_valid = True
            except bluetooth.btcommon.BluetoothError:
                print("Bluetooth recieve error")
                self.bt_connect()
            print "received [%s]" % data

    def bt_connect(self):
        try:
            self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.bind(("",port))
            self.sock.listen(1)
            self.client_sock,address = server_sock.accept()
            print("Accepted connection from %s" % self.address)
            self.connected = True
        except bluetooth.btcommon.BluetoothError as e:
            print ("Bluetooth error: %s" % e)
            time.sleep(2)
            connected = False
            self.bt_connect()

if __name__ == '__main__':
    therm = BTThermometer(BD_ADDR, PORT, SAMPLE_FREQ)
    therm.run()
    