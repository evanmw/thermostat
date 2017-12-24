import time
import wiringpi

ON_PWM = 1900
OFF_PWM = 1100
SERVO_GPIO_PIN = 18

CONTROL_PERIOD = 30 # seconds
DEAD_BAND = 2 # degrees C

class Controller():
    def __init__(self, name, data):
        self.name = name
        self.received_kill = False
        self.temps = data.temps
        self.get_setpoint = data.get_setpoints
        self.weights = data.SETPOINT_WEIGHT_OPTIONS
        
        self.last_update_time = time.time()
        
        # setup servo
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(SERVO_GPIO_PIN, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)

    def turn_on(self):
        wiringpi.pwmWrite(SERVO_GPIO_PIN, ON_PWM)

    def turn_off(self):
        wiringpi.pwmWrite(SERVO_GPIO_PIN, OFF_PWM)

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
            averages[key] = sum / n_samples
        weight_index = get_setpoint()[1]
        weight = self.weights[weight_index]

        control_temp = (1-weight)*averages['local'] + \  ####TODO make flexible
                       weight*averages['bt_therm']
        return control_temp
    
    def update(self):
        setpoint_temp = self.get_setpoint()[0]
        control_temp = self.get_control_temp()

        if (control_temp - setpoint_temp) > (DEAD_BAND / 2):
            self.turn_off()

        if (setpoint_temp - control_temp) > (DEAD_BAND / 2):
            self.turn_on()
            
    def run(self):
        while not received_kill:
            if time.time() - self.last_update_time > CONTROL_PERIOD:
                self.update()
                self.last_update_time = time.time()

if __name__=='__main__':
    pass
