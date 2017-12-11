import os
import time
import glob
import logging
from datetime import datetime

class LocalThermometer():
    def __init__(self, name, data, data_lock, sample_freq=1):
        self.kill_recieved = False
        self.sample_freq = sample_freq

        self.data = data
        self.data_lock = data_lock
        self.name = name # threading.current_thread()

        with self.data_lock:
            self.data[self.name] = []

        # Enable temp sensor
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Find device folder
        base_dir = '/home/evan/thermostat/test_local_therm/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'


    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

    def sample(self):
        temp_c, temp_f = self.read_temp()
        with self.data_lock:
            self.data[self.name].append((datetime.now(), temp_c))

    def run(self):
        while not self.kill_recieved:
            self.sample()
            time.sleep(self.sample_freq)

        logging.warn("Recieved kill")


if __name__ == '__main__':
    pass