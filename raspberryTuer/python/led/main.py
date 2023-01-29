#!/usr/bin/env python3

import time
import threading
from rpi_ws281x import *
import argparse
import paho.mqtt.client as mqtt
import json


# LED strip configuration:
LED_COUNT      = 445 #386      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

class LED:
    def __init__(self, color):
        self.color = color
        
    def set_color(self, color):
        self.color = color


#-------------------------------------------------
#            Aktualisierungs Thread

def neopixel_thread(strip, leds):
    print("Neopixel Thread started")
    while True:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, leds[i].color)
        strip.show()

# MQTT Message 
# Callback-Funktion für eingehende Nachrichten
def on_message(client, userdata, message):
    # Nachricht empfangen und als JSON-Dictionary decodieren
    msg = json.loads(message.payload.decode())
    # Farbwerte aus dem Dictionary extrahieren
    r, g, b = msg["color"]
    # Farbwerte ausgeben
    for led in tuer:
        led.set_color(Color(r,g,b))

#-------------------------------------------------
#             Animations Thread

#-------------------------------------------------
#           Beispiel Animationen

# Define functions which animate LEDs in various ways.
def colorWipe(leds, color, wait_ms=25):
    """Wipe color across display a pixel at a time."""
    for led in leds:
        led.color = color
        time.sleep(wait_ms/1000.0)

def theaterChase(leds, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(color)            
            time.sleep(wait_ms/1000.0)
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(Color(0,0,0))

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

def rainbow(leds, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(len(leds)):
            leds[i].set_color(wheel((i+j) & 255))
        time.sleep(wait_ms/1000.0)

def rainbowCycle(leds, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(len(leds)):
            leds[i].set_color(wheel(min(255,(int(i * 256 / len(leds)) + j) & 255)))
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(leds, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(wheel((i+j) % 255))
            
            time.sleep(wait_ms/1000.0)
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(0)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    #LED Array
    leds = []

    #LEDs mit 0 initialisieren
    for i in range(strip.numPixels()):
        leds.append(LED(Color(0,0,0)));

    # LED Array Wagen
    wagen=[]
    for i in range(28,414):
        wagen.append(leds[i])

    # LED Array Wagen
    tuer=[]
    for i in range(0,28):
        tuer.append(leds[i])
    for i in range(414,len(leds)-1):
        tuer.append(leds[i])

    #MQTT-Client Thread starten
    client = mqtt.Client()
    client.on_message = on_message

    # Verbindung zum MQTT-Broker herstellen
    client.connect("192.168.178.105", 1883)

    # Thema abonnieren
    client.subscribe("tuer")

    # Nachrichten empfangen
    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.start()

    #LED refresh Thread starten
    neopixel_refresh_thread = threading.Thread(target=neopixel_thread, args=(strip,leds,))
    neopixel_refresh_thread.start()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            print ('Color wipe animations.')
            colorWipe(wagen, Color(255, 0, 0))  # Red wipe
            colorWipe(wagen, Color(0, 255, 0))  # Blue wipe
            colorWipe(wagen, Color(0, 0, 255))  # Green wipe
            print ('Theater chase animations.')
            for i in range(10):
                theaterChase(wagen, Color(127, 127, 127))  # White theater chase
                theaterChase(wagen, Color(127,   0,   0))  # Red theater chase
                theaterChase(wagen, Color(  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            rainbow(wagen)
            rainbowCycle(wagen)
            theaterChaseRainbow(wagen)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(leds, Color(0,0,0), 10)
            time.sleep(1)
