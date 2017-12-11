import bluetooth
import logging
from datetime import datetime
import threading

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

PORT = 1

class BTThermometerServer():
    def __init__(self, name, port, data, data_lock):
        self.name = name
        self.data = data
        self.data_lock = data_lock
        self.connected = False
        self.port = PORT
        self.server_sock = None
        self.client_sock = None
        self.bt_connect()
        self.kill_recieved = False

        with self.data_lock:
            self.data[self.name] = []

    def run(self):
        while not self.kill_recieved:
            recieved = ""
            recieved_valid = False
            try:
                recieved = self.client_sock.recv(1024)
                recieved_valid = True
            except bluetooth.btcommon.BluetoothError:
                logging.debug("Bluetooth recieve error")
                self.bt_connect()

            if recieved != "":
                recieved = recieved.split(',')
                recieved_parsed = (datetime.strptime(recieved[0], '%b %d %Y %I:%M%p'), recieved[1])
                with self.data_lock:
                    self.data[self.name].append(recieved_parsed)

        logging.warn("Recieved kill")
        self.client_sock.close()
        self.server_sock.close()

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
            logging.debug("Accepted connection from %s" % str(address))
            self.connected = True
        except bluetooth.btcommon.BluetoothError as e:
            logging.debug ("Bluetooth error: %s" % e)
            time.sleep(2)
            connected = False
            self.bt_connect()

if __name__ == '__main__':
    try:
        therm = BTThermometerServer(PORT)
        therm.run()
    except KeyboardInterrupt:
        therm.kill_recieved = True

    