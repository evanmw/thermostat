import logging
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class PiInterface():
    def __init__(self, name, data): #temps, temp_lock, get_setpoint, setpoint_lock):
        self.kill_received = False
        self.name = name
        self.temps = data.temps
        self.temp_lock = data.temps_lock
        self.get_setpoint = data.get_setpoint
        self.setpoint_lock = data.setpoint_lock

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.WARNING)

        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        self.font = ImageFont.truetype('resources/OpenSans-Regular.ttf', size=55)
        self.s_font = ImageFont.truetype('resources/OpenSans-Regular.ttf', size=40)
        
    def scrawl(self, text, font, x, y):
        text = str(text)
        self.draw.text((x-font.getoffset(text)[0], 0-font.getoffset(text)[1]),
                       text, font=font, fill=255)
            
    def run(self):
        while not self.kill_received:
            temp = 0
            with self.temp_lock:
                if len(self.temps["local"]) < 1:
                    continue
                temp = self.temps["local"][-1]
            
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            self.scrawl(int(round(temp[1])), self.font, 0, 0)
            self.scrawl(self.get_setpoint()[0], self.s_font, 70, 20)

            self.disp.image(self.image)
            self.disp.display()
            time.sleep(0.1)

        logging.warn("Received kill")
