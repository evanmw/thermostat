import logging
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class PiInterface():
    def __init__(self, name, temps, temp_lock, get_setpoint, setpoint_lock):
        self.name = name
        self.temps = temps
        self.temp_lock = temp_lock
        self.get_setpoint = get_setpoint
        self.setpoint_lock = setpoint_lock
        self.setpoint = self.update_setpoint()

        self.DC = 23
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)

    def update_setpoint(self):
        with self.setpoint_lock:
            self.setpoint = self.get_setpoint()