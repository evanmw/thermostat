import schedule
import time
import threading
import logging

class ThermostatSchedule():
    def __init__(self, name, data): #set_setpoint, setpoint_lock):
        self.name = name
        self.kill_received = False
        self.set_setpoint = data.set_setpoint
        self.setpoint_lock = data.setpoint_lock
        self.setpoint = data.get_setpoint
        self.sheshule = schedule.Scheduler()


        self.sheshule.every(15).seconds.do(self.set_setpoint, 70, "local")
        self.sheshule.every(25).seconds.do(self.set_setpoint, 50, "bt_therm")

    def run(self):
        while not self.kill_received:
            self.sheshule.run_pending()
            time.sleep(1)
        logging.warn("received kill")

if __name__ == '__main__':
    pass
