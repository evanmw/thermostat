import schedule
import time
import datetime
import threading
import logging
import csv
import os
import string

SCHEDULE_FILE_PATH='/home/pi/thermostat/python/thermster/resources/schedule.txt'
SCHEDULE_CHECK_PERIOD = 10 # seconds

class ThermostatSchedule():
    def __init__(self, name, data):
        self.name = name
        self.kill_received = False
        self.set_setpoint = data.set_setpoint
        self.setpoint_lock = data.setpoint_lock
        self.setpoint = data.get_setpoint
        self.sheshule = schedule.Scheduler()

        self.last_update_time = 0.0
        self.update_schedule()
        
    def update_schedule(self):
        modified_time = os.path.getmtime(SCHEDULE_FILE_PATH)
        if modified_time > self.last_update_time:
            self.sheshule = self.read_schedule()
            self.last_update_time = time.time()
        
    def read_schedule(self):
        with open(SCHEDULE_FILE_PATH, 'rb') as schedule_file:
            # make a new schedule object
            new_shesh = schedule.Scheduler()
            for entry in schedule_file:
                parsed_entry = self.parse_schedule(entry)
                if (parsed_entry):
                    self.set_schedule(new_shesh, parsed_entry)
            return new_shesh
                
    def parse_schedule(self, entry):
        entry = entry.split('#', 1)[0]  # cut out any comments
        entry = entry.split()  # turn entry into a list
        if len(entry) != 4:
            return False
        try:
            set_time = time.strptime(entry[1], "%I:%M%p") # convert to time object
        except:
            logging.warn("Failed to parse schedule time: %s" % entry[1])
            return False
        days = list(string.upper(entry[0]))
        set_temp = float(entry[2])
        set_weight = min(max(int(round(float(entry[3]))), 0), 4)
        schedule_entry_data = {'days': days,
                               'time': set_time,
                               'temp': set_temp,
                               'weight': set_weight}
        return schedule_entry_data

    def set_schedule(self, shesh, entry_data):
        t = time.strftime("%H:%M", entry_data['time'])   # convert to 24 hour time
        temp = entry_data['temp']
        weight = entry_data['weight']
        for day in entry_data['days']:
            if day == 'M':
                shesh.every().monday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'T':
                shesh.every().tuesday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'W':
                shesh.every().wednesday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'R':
                shesh.every().thursday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'F':
                shesh.every().friday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'S':
                shesh.every().saturday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'U':
                shesh.every().sunday.at(t).do(self.set_setpoint, temp, weight)
            else:
                logging.warn("Invalid day character, %s" % day)
            
    def run(self):
        cycles = 0
        while not self.kill_received:
            if cycles % SCHEDULE_CHECK_PERIOD == 0:
                self.update_schedule()
                cycles = 0
            self.sheshule.run_pending()
            cycles += 1
            time.sleep(1)
        logging.warn("received kill")

if __name__ == '__main__':
    pass
