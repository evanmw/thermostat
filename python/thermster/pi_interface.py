import logging
import time
import datetime
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
        self.PRESS_DURATION = 0.07 # seconds
        self.REMOTE_REPORT_PERIOD = 2 # seconds
        
        self.fahrenheit = False
        
        self.REQ_CYCLES = self.PRESS_DURATION * self.RUN_RATE
        self.LOOP_SLEEP = 1/self.RUN_RATE
        # button NAME: [pin, cur_cycles, callback]
        buttons = {'Lpin': [27, 0, self.left_cb],
                   'Rpin': [23, 0, self.right_cb],
                   'Cpin': [ 4, 0, None],
                   'Upin': [17, 0, self.up_cb],
                   'Dpin': [22, 0, self.down_cb],
                   'Apin': [ 5, 6, self.a_cb]   ,
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
        self.WEIGHT_OPTIONS = data.WEIGHT_OPTIONS
        
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

        self.font = ImageFont.truetype('resources/OpenSans-Regular.ttf', size=33)
        self.s_font = ImageFont.truetype('resources/OpenSans-Regular.ttf', size=28)

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

    def right_cb(self):
        temp_sp, weight = self.get_setpoint()
        weight = weight-1
        if weight < 0:
            weight = len(self.WEIGHT_OPTIONS)-1
        self.set_setpoint(temp_sp, weight)

    def left_cb(self):
        temp_sp, weight = self.get_setpoint()
        weight = weight+1
        if weight > len(self.WEIGHT_OPTIONS)-1:
            weight = 0
        self.set_setpoint(temp_sp, weight)

    def a_cb(self):
        self.fahrenheit = not self.fahrenheit

    def scrawl(self, text, font, x, y):
        text = str(text)
        self.draw.text((x-font.getoffset(text)[0], y-font.getoffset(text)[1]),
                       text, font=font, fill=255)

    def c_to_f(self, c):
        if type(c) == type('--'):
            return c
        return 1.8*c+32

    def round_temp(self, c):
        if type(c) == type('--'):
            return c
        return round(c, 1)

    def draw_weight_indicator(self):
        x = 71
        indicator_len = 24
        screen_height = 60

        max_y_top = screen_height - indicator_len        
        temp, weight_index = self.get_setpoint()
        weight = self.WEIGHT_OPTIONS[weight_index]
        y_top = max_y_top * (1 - weight)
        y_bottom = y_top + indicator_len
        
        self.draw.line([(x, y_top), (x, y_bottom)], 1, 1)
        
    
    def run(self):
        while not self.kill_received:
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

            # get the temperatures
            local_temp = 0.0
            remote_temp = 0.0

            with self.temp_lock:
                if len(self.temps["local"]) < 1:
                    continue
                last_local_time, local_temp = self.temps["local"][-1]
                if len(self.temps["bt_therm"]) > 1:  ###TODO clean up logic
                    last_remote_time, remote_temp = self.temps["bt_therm"][-1]
                    if datetime.datetime.now() - last_remote_time > datetime.timedelta(seconds=2*self.REMOTE_REPORT_PERIOD):
                        remote_temp = ' :('

            # get the setpoint
            setpoint_temp, setpoint_therm = self.get_setpoint()
            
            # convert to desired display units
            if (self.fahrenheit):
                local_temp = self.c_to_f(local_temp)
                remote_temp = self.c_to_f(remote_temp)
                setpoint_temp = int(round(self.c_to_f(setpoint_temp)))

            # round temps to 1 decimal place
            local_temp = self.round_temp(local_temp)
            remote_temp = self.round_temp(remote_temp)

            # now draw    
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            # current temps
            self.scrawl(local_temp, self.font, 0, 0)
            self.scrawl(remote_temp, self.font, 0, 35)

            # setpoint thermometer weight
            self.draw_weight_indicator()
            #            self.draw.line([(71, 0), (71, 24)], 1, 1)

            # setpoint temperature
            self.scrawl(setpoint_temp, self.s_font, 86, 5)

            self.disp.image(self.image)
            self.disp.display()
            time.sleep(self.LOOP_SLEEP)

        logging.warn("Received kill")
