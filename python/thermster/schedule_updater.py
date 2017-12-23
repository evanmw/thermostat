import os
import time
import logging
from thermostat_scheduler import ThermostatScheduler

SCHEDULE_CHECK_PERIOD = 10 # seconds

class ScheduleUpdater():
    def __init__(self, name, data):
        self.name = name
        self.kill_received = False
        self.sheshule = data.sheshule
        self.shesh_lock = data.shesh_lock
        self.shesh_file_path = data.SCHEDULE_FILE_PATH

        self.scheduler = ThermostatScheduler(self.sheshule,
                                             self.shesh_lock,
                                             self.shesh_file_path,
                                             data.set_setpoint)
        self.last_update_time = 0.0
        
        self.scheduler.update_from_file()

    def update_needed(self):
        modified_time = os.path.getmtime(self.shesh_file_path)
        if modified_time > self.last_update_time:
            if self.scheduler.update_from_file():
                self.last_update_time = time.time()
                
    def run(self):
        cycles = 0
        while not self.kill_received:
            if cycles % SCHEDULE_CHECK_PERIOD == 0:
                if self.update_needed():
                    self.scheduler.update_from_file()
                cycles = 0
            with self.shesh_lock:
                self.sheshule.run_pending()
            cycles += 1
            time.sleep(1)
        logging.warn("received kill")

if __name__ == '__main__':
    pass
