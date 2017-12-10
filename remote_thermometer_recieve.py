import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

PORT = 1

class BTThermometerServer():
    def __init__(self, port):
        self.connected = False
        self.port = PORT
        self.server_sock = None
        self.client_sock = None
        self.bt_connect()

    def run(self):
        while (1):
            data = ""
            data_valid = False
            try:
                data = self.client_sock.recv(1024)
                data_valid = True
            except bluetooth.btcommon.BluetoothError:
                print("Bluetooth recieve error")
                self.bt_connect()
            print "received [%s]" % data

    def bt_connect(self):
        try:
            if self.server_sock is not None:
                self.server_sock.close()
            if self.client_sock is not None:
                self.client_sock.close()
            self.server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)
            self.client_sock,address = self.server_sock.accept()
            print("Accepted connection from %s" % address)
            self.connected = True
        except bluetooth.btcommon.BluetoothError as e:
            print ("Bluetooth error: %s" % e)
            time.sleep(2)
            connected = False
            self.bt_connect()

if __name__ == '__main__':
    therm = BTThermometerServer(PORT)
    therm.run()
    