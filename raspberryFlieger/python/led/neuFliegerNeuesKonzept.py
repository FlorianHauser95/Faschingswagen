#!/usr/bin/env python3

import time
from neopixel import *
import argparse
from xml.dom import minidom
import RPi.GPIO as GPIO
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
from thread import start_new_thread



#SPI Configure

# Configure the count of pixels:
PIXEL_COUNT = 50
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

#LED Configure

# LED strip configuration:
LED_COUNT      = 120      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def loadChannel():
    try:
        DMXData = minidom.parse("Artnet.xml")
        return DMXData
    except KeyboardInterrupt:
        exitNow = True
    except:
        if args.clear:
            exitNow = True

def getChannelValue(DMXDataV, DMXChannel=1, oldValue=0):
    try:
        dmxxlrname = str("DMX" + str(DMXChannel-1))
        nameD = DMXDataV.getElementsByTagName(dmxxlrname)[0]
        return int(nameD.firstChild.data)
    except KeyboardInterrupt:
        exitNow = True
    except:
        return oldValue


def wheelA(pos):
    if pos < 85:
        return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
        
    for i in range(pixels.count()):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels.set_pixel(i, wheel(((i * 256 // pixels.count())) % 256) )
        pixels.show()
        if wait_ms > 0:
            time.sleep(wait_ms/1000.0)

def init():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    
    for i in range(pixels.count()):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(0, 0, 0))


def tragflaechenLicht():
    strip.setPixelColor(0, Color(0, 255, 0))
    strip.setPixelColor(1, Color(0, 255, 0))
    strip.setPixelColor(2, Color(0, 0, 0))
    strip.setPixelColor(3, Color(0, 0, 0))
    strip.setPixelColor(4, Color(0, 0, 0))
    strip.setPixelColor(5, Color(100, 100, 100))

    strip.setPixelColor(6, Color(255, 0, 0))
    strip.setPixelColor(7, Color(255, 0, 0))
    strip.setPixelColor(8, Color(0, 0, 0))
    strip.setPixelColor(9, Color(0, 0, 0))
    strip.setPixelColor(10, Color(0, 0, 0))
    strip.setPixelColor(11, Color(100, 100, 100))

def tragflaechenBlinker(hell=0):
    strip.setPixelColor(2, Color(hell, hell, hell))
    strip.setPixelColor(3, Color(hell, hell, hell))
    strip.setPixelColor(4, Color(hell, hell, hell))

    strip.setPixelColor(9, Color(hell, hell, hell))
    strip.setPixelColor(8, Color(hell, hell, hell))
    strip.setPixelColor(10, Color(hell, hell, hell))

def rumpfBlinker(hell=0):
    pixels.set_pixel(36, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(37, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(38, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(39, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )

    pixels.set_pixel(40, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(41, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(42, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    pixels.set_pixel(43, Adafruit_WS2801.RGB_to_color(hell, 0, 0) )
    
    pixels.set_pixel(44, Adafruit_WS2801.RGB_to_color(hell, hell, hell) )
    pixels.set_pixel(45, Adafruit_WS2801.RGB_to_color(hell, hell, hell) )
    pixels.set_pixel(46, Adafruit_WS2801.RGB_to_color(hell, hell, hell) )
    pixels.set_pixel(47, Adafruit_WS2801.RGB_to_color(hell, hell, hell) )


#Strip Gruen Rot Blau
#Pixels Rot Gruen Blau

def thDMX():
    while True:
        DMXdaten = loadChannel()

        global K1
        global K2
        global K3
        global K4

        #DMX Daten lesen
        #Rot
        K1 = getChannelValue(DMXdaten,250, K1)
        #Gruen
        K2 = getChannelValue(DMXdaten,251, K2)
        #Blau
        K3 = getChannelValue(DMXdaten,252, K3)
        #Effekt
        K4 = getChannelValue(DMXdaten,253, K4)

        time.sleep(50/1000.0)


#Programm
if __name__ == "__main__":
    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!

    #strip
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    K1=0
    K2=0
    K3=0
    K4=0

    #start_new_thread(thDMX,())

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    init()
    strip.show()
    time.sleep(50/1000.0)
    pixels.show()

    exitNow = False

    #Counter
    cFluegl = 0
    o=0
    oo=0
    ooo=8
    oooo=8
    j=0

    #Schritt 3
    c=0

    #schritt 4
    b=0

    l=0

    schritt=1

    while True:

        if K4 < 10:
            K1 = 255
            K2 = 0
            K3 = 0

        if schritt == 1:
            for i in range(strip.numPixels()-5):
                strip.setPixelColor(i, Color(0, 255, 0))
            c=c+1
            if c == (1500):
                c=0
                schritt=2
        
        if schritt == 2:
            for i in range(strip.numPixels()-5):
                strip.setPixelColor(i, wheel((int(i * 256 / (strip.numPixels()-5) + j) & 255)))
            j=j+1
            if j == 257:
                j=0

            c=c+1
            if c == (1000):
                c=0
                schritt=3

        #Schritt 3

        if schritt == 3:
            for i in range(strip.numPixels()-5):
                if i > c:
                    strip.setPixelColor(i, Color(0, 0, 255))
                if i < c:
                    strip.setPixelColor(i, Color(0, 255, 0))

            c=c+1
            if c == (strip.numPixels()):
                c=0
                schritt=4


        if schritt == 4:
            for i in range(strip.numPixels()-5):
                if i > c:
                    strip.setPixelColor(i, Color(0, 255, 0))
                if i < c:
                     strip.setPixelColor(i, Color(255, 0 , 0))

            c=c+1
            if c == (strip.numPixels()):
                c=0
                schritt=5


        if schritt == 5:
            for i in range(strip.numPixels()-5):
                if i > c:
                    strip.setPixelColor(i, Color(255, 0, 0))
                if i < c:
                     strip.setPixelColor(i, Color(0, 0, 255))

            c=c+1
            if c == (strip.numPixels()):
                c=0
                l=l+1
                schritt=3
                if l==7:
                    l=0
                    schritt=1
                
                

       

        #Triebwerke
        for i in range(36):
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(255, 0, 255) )

        o=o+1
        if o == 9:
            o=0
        oo=oo+1
        if oo == 9:
            oo=0
        ooo=ooo-1
        if ooo < 0:
            ooo=8
        oooo=oooo+1
        if oooo == 9:
            oooo=0

        pixels.set_pixel(o, Adafruit_WS2801.RGB_to_color(255, 255, 255))
        pixels.set_pixel(oo+9, Adafruit_WS2801.RGB_to_color(255, 255, 255))
        pixels.set_pixel(ooo+18, Adafruit_WS2801.RGB_to_color(255, 255, 255))
        pixels.set_pixel(oooo+27, Adafruit_WS2801.RGB_to_color(255, 255, 255))
           

        tragflaechenLicht()

        #Beleuchtung Fluegel
        if cFluegl <= 10 or cFluegl >= 12:
            tragflaechenBlinker(0)

        #Blinken am Fluegel ein
        if cFluegl > 10 and cFluegl < 12:
            tragflaechenBlinker(255)

        #Beleuchtung Rumpf aus
        if cFluegl <= 25 or cFluegl >= 27:
            rumpfBlinker(0)

        #Blinken Rumpf ein
        if cFluegl > 25 and cFluegl < 27:
            rumpfBlinker(255)

        if cFluegl >= 27:
            cFluegl = 0

        #Daten uebergeben an Stripes und NeoPixel
        strip.show()
        time.sleep(50/1000.0)
        pixels.show()
        
        cFluegl = cFluegl + 1
        #flieger()

