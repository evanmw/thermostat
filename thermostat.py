import time
import threading
from remote_thermometer_recieve import BTThermometerServer

PORT = 1

class Thermostat():
    def __init__(self):
        self.temps = {}

        # add 
        self.remote_therm = BTThermometerServer(PORT)
        self.remote_stat_thread = threading.Thread(target=self.remote_therm.run)


if __name__=='__main__':
    thermostat = Thermostat()

