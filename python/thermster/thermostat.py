import time
import threading
import logging
from collections import deque
from remote_thermometer_receive import BTThermometerServer
from local_thermometer import LocalThermometer
from thermostat_schedule import ThermostatSchedule
from pi_interface import PiInterface

PORT = 1

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


'''
Temperature data stored in ThermostatData.temps
Takes the form:

{ThermOneName: [(t1, T1), (t2, T2)], ThermTwoName: [(t1, T1), (t2,T2)]}
'''

class ThermostatData():
    def __init__(self):

        # Constants
        self.MAX_TEMP = 35  # C
        self.MIN_TEMP = 10


        self.temps = {}
        self.temps_lock = threading.RLock()
        self.setpoint = (21, "local")
        self.setpoint_lock = threading.RLock()

    def set_setpoint(self, temp, thermostat):
        with self.setpoint_lock:
            setpoint_temp = int(round(max(min(temp, self.MAX_TEMP), self.MIN_TEMP)))
            self.setpoint = (setpoint_temp, thermostat)

    def get_setpoint(self):
        with self.setpoint_lock:
            return self.setpoint
        
class Thermostat():
    def __init__(self):
        self.kill_received = False
        self.data = ThermostatData()

        # add threads
        self.thread_objects = [BTThermometerServer("bt_therm", PORT, self.data),
                               LocalThermometer("local", self.data,
                                                sample_freq=0.17),
                               ThermostatSchedule("schedule", self.data),
                               PiInterface("pi_interface", self.data)]
        self.threads = []
        for obj in self.thread_objects:
            self.threads.append(threading.Thread(name=obj.name, target=obj.run))
            self.threads[-1].start()
        logging.debug("Threads started")

    def run(self):
        while not self.kill_received:
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
