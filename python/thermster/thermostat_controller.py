import time
import RPi.GPIO as GPIO
import logging

ON_PWM = 1.9  # milliseconds
OFF_PWM = 1.1 # milliseconds

PWM_FREQUENCY = 50 #HZ
ON_DUTY_CYCLE = ON_PWM * PWM_FREQUENCY / 10  # = millisec * (1000/Hz) * 100
OFF_DUTY_CYCLE = OFF_PWM * PWM_FREQUENCY / 10
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
	
        # setup servo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_GPIO_PIN, GPIO.OUT)
        self.servo = GPIO.PWM(SERVO_GPIO_PIN, 50)
        self.servo.start(OFF_DUTY_CYCLE)

    def turn_on(self):
        self.servo.ChangeDutyCycle(ON_DUTY_CYCLE)

    def turn_off(self):
        self.servo.ChangeDutyCycle(OFF_DUTY_CYCLE)

    def get_control_temp(self):
        average_time = time.time() - CONTROL_PERIOD ######TODO convert to datetime object
        averages = {}
        for key, therm in list(self.temps.items()):
            n_samples = 0
            sum = 0.0
            while therm[-n_samples][0] > average_time:
                sum += therm[-n_samples][1]
                n_samples += 1
                if n_samples > len(therm)-1:
                    break
            averages[key] = sum / n_samples      ####TODO check that there's >0 points
        weight_index = get_setpoint()[1]         ### TODO define behavior if no current data
        weight = self.weights[weight_index]

        control_temp = (1-weight)*averages['local'] + \
                       weight*averages['bt_therm']       ####TODO make flexible
        return control_temp
	return 15.0

    def update(self):
	logging.warn("running control update")
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
