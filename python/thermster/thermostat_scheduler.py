import schedule
import time
import datetime
import threading
import logging
import string

class ThermostatScheduler():
    def __init__(self, sheshule, sheshule_lock, sheshule_file_path, set_setpoint):
        self.sheshule = sheshule
        self.shesh_lock = sheshule_lock
        self.shesh_file_path = sheshule_file_path
        self.set_setpoint = set_setpoint
        
    def update_from_file(self):
        entries = self.read_schedule()
        new_shesh = self.construct_schedule(entries)
        if self.update_schedule(new_shesh):
            return True
        return False
                
    def update_schedule(self, new_sheshule):
        with self.shesh_lock:
            self.sheshule = new_sheshule
            return True
        return False
                
    def read_schedule(self):
        with open(self.shesh_file_path, 'rb') as schedule_file:
            entries = []
            for entry in schedule_file:
                parsed_entry = self.parse_schedule_entry(entry)
                if (parsed_entry):
                    entries.append(parsed_entry)
            return entries
               
    def parse_schedule_entry(self, entry):
        entry = entry.split('#', 1)[0]  # cut out any comments
        entry = entry.split()  # turn entry into a list
        if len(entry) != 4:
            return False
        try:
            set_time = time.strptime(entry[1], "%I:%M%p") # convert to time object
            set_time = time.strftime("%H:%M", set_time)   # convert to 24 hour time
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

    def construct_schedule(self, entries):
        new_shesh = schedule.Scheduler()
        for entry in entries:
            self.set_schedule_entry(new_shesh, entry)
        return new_shesh
     
    def set_schedule_entry(self, shesh, entry_data):
        t = entry_data['time']
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
            
if __name__ == '__main__':
    pass
