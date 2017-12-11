import time
import threading
import logging
from remote_thermometer_recieve import BTThermometerServer
from local_thermometer import LocalThermometer

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

        # add threads
        self.thread_objects = [BTThermometerServer("bt_therm", PORT, self.temps, self.temps_lock),
                               LocalThermometer("local_therm", self.temps, self.temps_lock)]
        self.threads = []
        for obj in self.thread_objects:
            self.threads.append(threading.Thread(name=obj.name, target=obj.run))
            self.threads[-1].start()
        logging.debug("started")

    def run(self):
        while not self.kill_recieved:
            with self.temps_lock:
                logging.debug("remote samples: %s" % len(self.temps['bt_therm']))
                logging.debug("local samples: %s" % len(self.temps['local_therm']))
            time.sleep(1)

    def kill(self):
        for obj in self.thread_objects:
            obj.kill_recieved = True
        self.kill_recieved = True


if __name__=='__main__':
    try:
        thermostat = Thermostat()
        thermostat.run()
    except KeyboardInterrupt:
        logging.warn("Recieved kill")
        thermostat.kill()
