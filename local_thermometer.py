import os
import time
import logging
from datetime import datetime

class LocalThermometer():
    def __init__(self, data, data_lock):
        self.kill_recieved = False

        self.data = data
        self.data_lock = data_lock

        # Enable temp sensor
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Find device folder
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'


    def read_temp_raw(self):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

    def sample(self):
        temp_c, temp_f = self.read_temp()
        with self.data_lock:
            therm = threading.current_thread()
            self.data[therm].append((datetime.now(), temp_c))

    def run(self):
        while not self.kill_recieved:



if __name__ = __main__:
    pass



   
while True:
    print(read_temp())  
    time.sleep(1)
