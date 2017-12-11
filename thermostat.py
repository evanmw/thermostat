import time
import threading
import logging
from collections import deque
from remote_thermometer_receive import BTThermometerServer
from local_thermometer import LocalThermometer
from thermostat_schedule import ThermostatSchedule

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
        self.kill_received = False
        self.threads = {}

        self.setpoint = (72, "local") # (int(temp), str(thermometer))
        self.setpoint_lock = threading.RLock()

        # add threads
        self.thread_objects = [BTThermometerServer("bt_therm", PORT, self.temps, self.temps_lock),
                               LocalThermometer("local", self.temps, self.temps_lock),
                               ThermostatSchedule("schedule", self.set_setpoint, self.setpoint_lock)]
        self.threads = []
        for obj in self.thread_objects:
            self.threads.append(threading.Thread(name=obj.name, target=obj.run))
            self.threads[-1].start()
        logging.debug("Threads started")

    def set_setpoint(self, setpoint):
        with self.setpoint_lock:
            self.setpoint = setpoint

    def run(self):
        while not self.kill_received:
            logging.debug("setpoint: %s" % str(self.setpoint))
            time.sleep(1)

    def kill(self):
        for obj in self.thread_objects:
            obj.kill_received = True
        self.kill_received = True


if __name__=='__main__':
    try:
        thermostat = Thermostat()
        thermostat.run()
    except KeyboardInterrupt:
        logging.warn("received kill")
        thermostat.kill()
