# https://docs.micropython.org/en/latest/esp8266/tutorial/neopixel.html
import machine
from neopixel import NeoPixel
import time

pin_np = 19 # GPIO
leds = 21
np = NeoPixel(machine.Pin(pin_np, machine.Pin.OUT), leds, bpp=3)

red = (255, 0, 0) # max 255
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
green_weak = (0, 10, 0)
yellow_weak = (5,5,0)
magenta_weak = (10,0,10)

def blink(speed,color1,color2): #change between two colors
    np.fill(color1); np.write()
    time.sleep_ms(speed); np.write()
    np.fill(color2); np.write()
    time.sleep_ms(speed); np.write()
    
a=10; arra=[a]; rain=[] #making intensity array for rainbow
for i in range(5):
    for j in range(5): arra.append(a-2); a-=2
    for j in range(5): arra.append(0)
    for j in range(5): arra.append(a+2); a+=2
for i in range(len(arra)-10):
    rain.append((arra[i],arra[i+10],arra[i+5]))
    
def rainbow(start):
    for i in range(leds):
        np[i]=rain[i+start];
        np.write()
        
def rainbow_run(speed):
    for i in range(10*leds):
        rainbow(i)
        time.sleep_ms(speed); np.write()
        
def run(speed,background,color):
    for i in range(leds):
        np.fill(background)
        np[i]=color; np.write()
        time.sleep_ms(speed); np.write()
    
def trapped(speed,background,color):
    run(speed,background,color)
    for i in range(1,leds+1):
        np.fill(background)
        np[leds-i]=color; np.write()
        time.sleep_ms(speed); np.write()
        
def Off():
    np.fill((0,0,0)); np.write()

if __name__ == "__main__":
	while True:
		
		#trapped(100,red,blue)
		#blink(10,yellow_weak,magenta_weak)
		#blink(1000,yellow_weak,magenta_weak)
		#blink(1000,yellow_weak,magenta_weak)

		#rainbow_run(100)
		Off()
		#ticks, turn off properly, create color b rown (impossible) 

