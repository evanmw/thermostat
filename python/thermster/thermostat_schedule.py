import schedule
import time
import threading
import logging

class ThermostatSchedule():
    def __init__(self, name, set_setpoint, setpoint_lock):
        self.name = name
        self.kill_received = False
        self.set_setpoint = set_setpoint
        self.setpoint_lock = setpoint_lock
        self.sheshule = schedule.Scheduler()


        self.sheshule.every(15).seconds.do(self.setpoint, 70, "local")
        self.sheshule.every(25).seconds.do(self.setpoint, 50, "bt_therm")


    def setpoint(self, temp, thermometer="local"):
        with self.setpoint_lock:
            self.set_setpoint((temp, thermometer))

    def run(self):
        while not self.kill_received:
            self.sheshule.run_pending()
            time.sleep(1)
        logging.warn("received kill")

if __name__ == '__main__':
    pass