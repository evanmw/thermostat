import os
import time
import glob
import logging
from collections import deque
from datetime import datetime
from thermometer import Thermometer

class LocalThermometer():
    def __init__(self, name, data, sample_freq=1):
        self.kill_received = False
        self.sample_freq = sample_freq

        self.temps = data.temps
        self.temp_lock = data.temps_lock
        self.name = name # threading.current_thread()

        with self.temps_lock:
            self.temps[self.name] = deque(maxlen=100000)

        self.thermometer = Thermometer()
            
    def sample(self):
        temp_c, temp_f = self.thermometer.read_temp()
        with self.temps_lock:
            self.temps[self.name].append((datetime.now(), temp_c))

    def run(self):
        while not self.kill_received:
            self.sample()
            time.sleep(self.sample_freq)

        logging.warn("received kill")


if __name__ == '__main__':
    pass
