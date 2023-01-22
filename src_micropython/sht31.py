# https://github.com/kfricke/micropython-sht31

from machine import I2C
import time

R_HIGH   = const(1)
R_MEDIUM = const(2)
R_LOW    = const(3)

class SHT31(object):
    """
    This class implements an interface to the SHT31 temprature and humidity
    sensor from Sensirion.
    """

    # This static map helps keeping the heap and program logic cleaner
    _map_cs_r = {
    	True: {
            R_HIGH : b'\x2c\x06',
            R_MEDIUM : b'\x2c\x0d',
            R_LOW: b'\x2c\x10'
            },
        False: {
            R_HIGH : b'\x24\x00',
            R_MEDIUM : b'\x24\x0b',
            R_LOW: b'\x24\x16'
            }
        }

    def __init__(self, i2c, addr=0x44):
        """
        Initialize a sensor object on the given I2C bus and accessed by the
        given address.
        """
        if i2c == None:
            raise ValueError('I2C object needed as argument!')
        self._i2c = i2c
        self._addr = addr

    def _send(self, buf):
        """
        Sends the given buffer object over I2C to the sensor.
        """
        self._i2c.writeto(self._addr, buf)

    def _recv(self, count):
        """
        Read bytes from the sensor using I2C. The byte count can be specified
        as an argument.
        Returns a bytearray for the result.
        """
        return self._i2c.readfrom(self._addr, count)

    def _raw_temp_humi(self, r=R_HIGH, cs=True):
        """
        Read the raw temperature and humidity from the sensor and skips CRC
        checking.
        Returns a tuple for both values in that order.
        """
        if r not in (R_HIGH, R_MEDIUM, R_LOW):
            raise ValueError('Wrong repeatabillity value given!')
        self._send(self._map_cs_r[cs][r])
        time.sleep_ms(50)
        raw = self._recv(6)
        return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

    def get_temp_humi(self, resolution=R_HIGH, clock_stretch=True, celsius=True):
        """
        Read the temperature in degree celsius or fahrenheit and relative
        humidity. Resolution and clock stretching can be specified.
        Returns a tuple for both values in that order.
        """
        t, h = self._raw_temp_humi(resolution, clock_stretch)
        if celsius:
            temp = -45 + (175 * (t / 65535))
        else:
            temp = -49 + (315 * (t / 65535))
        return temp, 100 * (h / 65535)


class Sensors_sht31:
    def __init__(self):
        self.i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq =10000)  # die Nummer x bei Pin bezieht sich auf GPx
        self.sensor_a_fix = SHT31(self.i2c, addr=0x45)
        self.sensor_b_cable = SHT31(self.i2c, addr=0x44)
        self.temperature_C_a = 0.0
        self.humidity_percent_a = 0.0
        self.temperature_C_b = 0.0
        self.humidity_percent_b = 0.0
    
    def measure(self, average_n = 1):
        temperature_C_a_average = 0.0
        humidity_percent_a_average = 0.0
        temperature_C_b_average = 0.0
        humidity_percent_b_average = 0.0
        for i in range(average_n):
            temperature_C_a, humidity_percent_a = self.sensor_a_fix.get_temp_humi()
            temperature_C_b, humidity_percent_b = self.sensor_b_cable.get_temp_humi()
            temperature_C_a_average += temperature_C_a
            humidity_percent_a_average += humidity_percent_a
            temperature_C_b_average += temperature_C_b
            humidity_percent_b_average += humidity_percent_b
        self.temperature_C_a = temperature_C_a_average / average_n
        self.humidity_percent_a = humidity_percent_a_average / average_n
        self.temperature_C_b = temperature_C_b_average / average_n
        self.humidity_percent_b = humidity_percent_b_average / average_n
    

import machine

sensors = Sensors_sht31()

if __name__ == "__main__":
    sensors.measure()
    wlan_helper.print_oled('A:%0.1fC %0.1f' % (sensors.temperature_C_a, sensors.humidity_percent_a) ,'%rF')
    wlan_helper.print_oled('B:%0.1fC %0.1f' % (sensors.temperature_C_b, sensors.humidity_percent_b) ,'%rF')
    wlan_helper.print_time_since_start_s()
