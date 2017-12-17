import logging
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class PiInterface():
    def __init__(self, name, data):

        # set these
        self.RUN_RATE = 20 # Hz
        self.PRESS_DURATION = 0.07 # second
        
        self.REQ_CYCLES = self.PRESS_DURATION * self.RUN_RATE
        self.LOOP_SLEEP = 1/self.RUN_RATE
        # button NAME: [pin, cur_cycles, callback]
        buttons = {'Lpin': [27, 0, None],
                   'Rpin': [23, 0, None],
                   'Cpin': [ 4, 0, None],
                   'Upin': [17, 0, self.up_cb],
                   'Dpin': [22, 0, self.down_cb],
                   'Apin': [ 5, 6, None],
                   'Bpin': [ 6, 0, None]}

        # put buttons into better format
        self.buttons = {}
        for name, button in list(buttons.items()):
            self.buttons[name] = {'pin': button[0], 'cycles': button[1], 'cb': button[2]}
        
        self.kill_received = False
        self.name = name
        self.temps = data.temps
        self.temp_lock = data.temps_lock
        self.get_setpoint = data.get_setpoint
        self.set_setpoint = data.set_setpoint

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

        # Set pins as innputs:
        GPIO.setmode(GPIO.BCM) 
        for key, button in list(self.buttons.items()):
            GPIO.setup(button['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

    def up_cb(self):
        temp_sp, therm = self.get_setpoint()
        self.set_setpoint(temp_sp+1, therm)

    def down_cb(self):
        temp_sp, therm = self.get_setpoint()
        self.set_setpoint(temp_sp-1, therm)
           
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

            # check for button input
            for key, button in list(self.buttons.items()):
                # if button is pressed, add to counter
                if not GPIO.input(button['pin']):
                    button['cycles'] += 1

                # is it time to run the callback?
                if button['cycles'] > self.REQ_CYCLES:
                    if not button['cb']:
                        continue
                    button['cb']()
                    button['cycles'] = 0  # reset cycles since cb
                
            # now draw    
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            self.scrawl(int(round(temp[1])), self.font, 0, 0)
            self.scrawl(self.get_setpoint()[0], self.s_font, 70, 20)

            self.disp.image(self.image)
            self.disp.display()
            time.sleep(self.LOOP_SLEEP)

        logging.warn("Received kill")
