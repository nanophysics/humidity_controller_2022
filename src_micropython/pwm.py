import machine

class Fan_pwm:
    def __init__(self, pin_GPx = 0, frequency_Hz = 25000): 
        self.fan_pwm = machine.PWM(machine.Pin(pin_GPx))
        self.fan_pwm.freq(frequency_Hz)
    def set_intensity(self, intensity = 0.2): # intensity 0.0...1.0
        intensity = 1.0 - intensity
        intensity_u16 = int(intensity * 2**16)
        intensity_u16 = max( 0, intensity_u16)
        intensity_u16 = min( 65535, intensity_u16)
        # print(intensity_u16)
        self.fan_pwm. duty_u16(intensity_u16)
        
class Fans_pwm:
    def __init__(self): 
        self.fan1 = Fan_pwm(pin_GPx = 0)
        self.fan2 = Fan_pwm(pin_GPx = 1)
    def set_intensity(self, intensity = 0.2): # intensity 0.0...1.0
        self.fan1.set_intensity(intensity)
        self.fan2.set_intensity(intensity)
        
fans = Fans_pwm()
fans.set_intensity(intensity = 0.00)
    
