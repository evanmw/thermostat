import time
import threading
import logging
from remote_thermometer_recieve import BTThermometerServer

PORT = 1

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


'''
Temperature data stored in Thermostat.temps
Takes the form:

{ThermOneName: [(t1, T1), (t2, T2)], ThermTwoName: [(t1, T1), (t2,T2)]}
'''

class Thermostat():
    def __init__(self):
        self.temps = {}
        self.temps_lock = threading.RLock()
        self.kill_recieved = False
        self.threads = {}

        # add 
        self.remote_therm = BTThermometerServer(PORT, self.temps, self.temps_lock)
        self.threads['bt_therm'] = \
            threading.Thread(name="bt_therm", target=self.remote_therm.run)
        for thread in self.threads.keys():
            self.threads[thread].start()
        logging.debug("started")

    def run(self):
        while not self.kill_recieved:
            time.sleep(1)

    def kill(self):
        for thread in self.threads.keys():
            self.threads[thread].kill_recieved = True
        self.kill_recieved = True


if __name__=='__main__':
    try:
        thermostat = Thermostat()
        thermostat.run()
    except KeyboardInterrupt:
        logging.warn("recieved kill")
        thermostat.kill()
