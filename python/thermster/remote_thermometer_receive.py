import bluetooth
import logging
from datetime import datetime
import threading
from collections import deque 

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

PORT = 1

class BTThermometerServer():
    def __init__(self, name, port, data):
        self.name = name
        self.temps = data.temps
        self.temps_lock = data.temps_lock
        self.connected = False
        self.port = PORT
        self.server_sock = None
        self.client_sock = None
        self.kill_received = False

        with self.temps_lock:
            self.temps[self.name] = deque(maxlen=100000)

    def run(self):
        while not self.kill_received:
            if not self.connected:
                self.bt_connect()
            received = ""
            received_valid = False
            try:
                received = self.client_sock.recv(1024)
                received_valid = True
            except bluetooth.btcommon.BluetoothError:
                logging.debug("Bluetooth receive error")
                self.bt_connect()

            if received != "":
                received = received.split(',')
                received_parsed = (datetime.strptime(received[0], '%b %d %Y %I:%M%p'), received[1])
                with self.temps_lock:
                    self.temps[self.name].append(received_parsed)

        logging.warn("received kill")
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
        therm.kill_received = True

    
