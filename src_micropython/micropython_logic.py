import time
import machine
import micropython
import neo_led
import sht31
import pwm

real_setup = True

def pyboard_init():
    if real_setup:
        neo_led.np.fill((0,0,0))
        neo_led.np.write()

def leds(color=(0,0,0)):
    if real_setup:
        neo_led.np.fill(color)
        neo_led.np.write()

def get_measurement(average_n = 1):
    if real_setup == True:
        sht31.sensors.measure(average_n = average_n)
        dict = {
            'humi_temp_C': sht31.sensors.temperature_C_a,
            'humi_humi_pRH': sht31.sensors.humidity_percent_a,
            'stage_temp_C': sht31.sensors.temperature_C_b,
            'stage_humi_pRH': sht31.sensors.humidity_percent_b,
        }
    else:
        dict = {
            'humi_temp_C': 25.4,
            'humi_humi_pRH': 75.3,
            'stage_temp_C': 26.3,
            'stage_humi_pRH': 77.9,
        }
    return dict

def set_fan_hum_intensity(value):
    pwm.fans_hum.set_fan_hum_intensity(value/100.0)

def set_fan_circ_intensity(value):
    pwm.fan_circ.set_intensity(value/100.0)
    if value < 0.1:
        pwm.fan_circ_on_off.set_intensity(1.0)
    else:
        pwm.fan_circ_on_off.set_intensity(0.0) # Schaltet sonst nicht komplett aus. Bastel.