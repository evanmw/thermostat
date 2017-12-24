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

    def write_file_from_dict(self, entries_dict):
        entries = entries_dict
        with self.shesh_lock:
            with open(self.shesh_file_path, 'w') as f:
                for entry in entries:
                    entry['temp'] = str(entry['temp'])
                    entry['weight'] = str(entry['weight'])
                    line = "%s %s %s %s\n" % (entry['days'], entry['time'], entry['temp'], entry['weight'])
                    f.write(line)
                
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
            logging.warn("Too many items in schedule entry")
            return False
        entry[0] = self.check_days(entry[0])
        entry[1] = self.check_time(entry[1])
        entry[2] = self.check_temp(entry[2])
        entry[3] = self.check_weight(entry[3])
        for item in entry:
            if not item:
                logging.warn("Error: Failed to parse schedule file")
                return False
        schedule_entry_data = {'days': entry[0],
                               'time': entry[1],
                               'temp': entry[2],
                               'weight': entry[3]}
        return schedule_entry_data

    def construct_schedule(self, entries):
        new_shesh = schedule.Scheduler()
        for entry in entries:
            self.set_schedule_entry(new_shesh, entry)
        return new_shesh
     
    def set_schedule_entry(self, shesh, entry_data):
        t = time.strptime(entry_data['time'], "%I:%M%p") # convert to time object
        t = time.strftime("%H:%M", t)   # convert to 24 hour time
        temp = entry_data['temp']
        weight = entry_data['weight']
        for day in entry_data['days']:
            if day == 'm':
                shesh.every().monday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 't':
                shesh.every().tuesday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'w':
                shesh.every().wednesday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'r':
                shesh.every().thursday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'f':
                shesh.every().friday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 's':
                shesh.every().saturday.at(t).do(self.set_setpoint, temp, weight)
            elif day == 'u':
                shesh.every().sunday.at(t).do(self.set_setpoint, temp, weight)
            else:
                logging.warn("Invalid day character, %s" % day)

    def check_days(self, days):
        if type(days) != type(unicode('string')) \
           and type(days) != type('string'):
            logging.warn("'days' not unicode or string")
            return False
        days = days.replace(" ", "")
        days = days.lower()
        days = list(set(days))
        valid_days = ['m', 't', 'w', 't', 'f', 's', 'u']
        for day in days:
            if day not in valid_days:
                logging.warn("%s: not a day" % day)
                return False
        scores = {'m': 1, 't': 2, 'w':3, 'r':4, 'f':5, 's':6, 'u':7}
        days = ''.join(sorted(days, key=lambda x: scores[x]))
        return days

    def check_time(self, t):
        if type(t) != type(unicode('string')) \
           and type(t) != type('string'):
            logging.warn("'time' not unicode or string")
            return False
        t = t.replace(" ", "")
        xm = t[-2:].lower()
        t = t[:-2]
        if xm != "am" and xm != "pm":
            return False
        if len(t) > 2 and t.count(':') == 0:
            return False
        if t.count(':') > 1:
            return False
        h_m = t.split(':')
        for ii in range(len(h_m)):
            if len(h_m[ii]) > 2:
                return False
            h_m[ii].zfill(2)
        if len(h_m) == 1:
            h_m.append('00')
        t = h_m[0] + ':' + h_m[1] + xm
        try:
            obj = time.strptime(t, "%I:%M%p") # convert to time object
        except:
            return False
        return t

    def check_temp(self, temp):
        try:
            temp = float(temp)
        except:
            return False
        # round to nearest .5 deg
        temp = round(temp / 0.5) * 0.5
        return str(temp)

    def check_weight(self, w):
        try:
            w = int(w)
        except:
            return False
        valid_weights = [0, 1, 2, 3, 4]
        if w not in valid_weights:
            return False
        return str(w)
            
if __name__ == '__main__':
    pass
