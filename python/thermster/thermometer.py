import os
import time
import glob
import logging

class Thermometer():
    def __init__(self, offset=0):
        # Enable temp sensor
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self.offset = float(offset)
        
        # Find device folder
        base_dir = '/sys/bus/w1/devices/'
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
            return temp_c + self.offset

if __name__ == '__main__':
    pass
