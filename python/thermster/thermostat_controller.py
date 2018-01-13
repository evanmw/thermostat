import time
import RPi.GPIO as GPIO
import logging
from datetime import datetime, timedelta

ON_PWM = 1.0  # milliseconds
OFF_PWM = 1.8 # milliseconds
DISABLE_PWM = 0.0

PWM_FREQUENCY = 50 #HZ
ON_DUTY_CYCLE = ON_PWM * PWM_FREQUENCY / 10  # = millisec * (1000/Hz) * 100
OFF_DUTY_CYCLE = OFF_PWM * PWM_FREQUENCY / 10
DISABLE_DUTY_CYCLE = DISABLE_PWM * PWM_FREQUENCY / 10
SERVO_GPIO_PIN = 18

CONTROL_PERIOD = 30 # seconds
DEAD_BAND = 2 # degrees C

class ThermostatController():
    def __init__(self, name, data):
        self.name = name
        self.kill_received = False
        self.temps = data.temps
        self.get_setpoint = data.get_setpoint
        self.weights = data.WEIGHT_OPTIONS

        self.last_update_time = time.time()
        self.state = "OFF"

        # setup servo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_GPIO_PIN, GPIO.OUT)
        self.servo = GPIO.PWM(SERVO_GPIO_PIN, 50)
        self.servo.start(OFF_DUTY_CYCLE)
        time.sleep(1)
        self.servo.ChangeDutyCycle(DISABLE_DUTY_CYCLE)

    def turn_on(self):
        if self.state != "ON":
            self.servo.ChangeDutyCycle(ON_DUTY_CYCLE)
            time.sleep(1)
            self.servo.ChangeDutyCycle(DISABLE_DUTY_CYCLE)
            self.state = "ON"

    def turn_off(self):
        if self.state != "OFF":
            self.servo.ChangeDutyCycle(OFF_DUTY_CYCLE)
            time.sleep(1)
            self.servo.ChangeDutyCycle(DISABLE_DUTY_CYCLE)
            self.state = "OFF"

    def get_control_temp(self):
        average_time = datetime.now() - timedelta(CONTROL_PERIOD)
        averages = {} # tuples: (valid_bit, average)
        for key, therm in list(self.temps.items()):
            n_samples = 0
            last_sample_time = datetime.now()
            sum = 0.0
            while last_sample_time > average_time:
                if n_samples < len(therm):
                    sum += therm[-n_samples][1]
                    n_samples += 1
                    last_sample_time = therm[-n_samples][0]
                else:
                    break
            if n_samples > 0:
                averages[key] = (True, sum / n_samples)
            else:
                averages[key] = (False, 0)
        weight_index = self.get_setpoint()[1]
        weight = self.weights[weight_index]
        #TODO Actually do something if one of the sources is invalid
        control_temp = (1-weight)*averages['local'][1] + \
                       weight*averages['bt_therm'][1]       ####TODO make flexible
        return control_temp

    def update(self):
        setpoint_temp = self.get_setpoint()[0]
        control_temp = self.get_control_temp()

        if (control_temp - setpoint_temp) > (DEAD_BAND / 2):
            self.turn_off()

        if (setpoint_temp - control_temp) > (DEAD_BAND / 2):
            self.turn_on()

    def run(self):
        while not self.kill_received:
            if time.time() - self.last_update_time > CONTROL_PERIOD:
                self.update()
                self.last_update_time = time.time()
        self.servo.stop()
        GPIO.cleanup()

if __name__=='__main__':
    pass
