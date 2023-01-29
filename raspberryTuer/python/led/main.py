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

#-------------------------------------------------
# MQTT Message 
# Callback-Funktion für eingehende Nachrichten
def on_message(client, userdata, message):
    # Nachricht empfangen und als JSON-Dictionary decodieren
    msg = json.loads(message.payload.decode())
     # Überprüfe, von welchem Topic die Nachricht stammt
    if message.topic == "tuer":
        #den aktuellen tuer Thread beenden und neu starten
        tuer_thread.stop()
        tuer_thread =  threading.Thread(target=tuer_programm,args=(tuer_links, tuer_rechts, message,))
        tuer_thread.start()
    elif message.topic == "wagen":
         #den aktuellen tuer Thread beenden und neu starten
        wagen_rechts_thread.stop()
        wagen_links_thread.stop()
        wagen_rechts_thread =  threading.Thread(target=wagen_programm,args=(wagen_rechts,message,))
        wagen_links_thread =  threading.Thread(target=wagen_programm,args=(wagen_links,message,))
        wagen_rechts_thread.start()
        wagen_links_thread.start()
    else:
        # Keine passende Verarbeitung gefunden
        print("Unbekanntes Topic empfangen:", message.topic)

#-------------------------------------------------
#             Animations Thread

def wagen_programm(leds, msg):
    # Farbwerte aus dem Dictionary extrahieren
    r, g, b = msg["color"]
    color=Color(r,g,b)
    # Programmart extrahieren
    prog = msg["program"]

    if prog == "colorWipe":
        print ('Color wipe')
        while True:
            colorWipe(leds, color)

    elif prog == "theaterChase":
        print ('Theater Chase.')
        while True:
            theaterChase(leds, color)

    elif prog == "rainbow":
        print ('Rainbow')
        while True:
            rainbow(leds)
        
    elif prog == "rainbowCycle":
        print ("Rainbow Cycle")
        while True:
            rainbowCycle(leds)

    elif prog == "theaterChaseRainbow":
        print ("Theater Chase Rainbow")
        while True:
            theaterChaseRainbow(leds)

def tuer_programm(leds_links, leds_rechts, msg):
    # Farbwerte aus dem Dictionary extrahieren
    r, g, b = msg["color"]
    color=Color(r,g,b)
    # Programmart extrahieren
    prog = msg["program"]

    # Farbwerte ausgeben
    for led in leds_links:
        led.set_color(Color(r,g,b))
    for led in leds_rechts:
        led.set_color(Color(r,g,b))

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
    wagen_links=[]
    for i in range(28,193):
        wagen.append(leds[i])
    wagen_rechts=[]
    for i in range(413,192,-1):
        wagen.append(leds[i])

    # LED Array Wagen
    tuer_links=[]
    for i in range(414,len(leds)-1):
        tuer_links.append(leds[i])
    tuer_rechts=[]
    for i in range(27,-1,-1):
        tuer_rechts.append(leds[i])
   

    #MQTT-Client Thread starten
    client = mqtt.Client()
    client.on_message = on_message

    # Verbindung zum MQTT-Broker herstellen
    client.connect("192.168.178.105", 1883)

    # Thema abonnieren
    client.subscribe("tuer")
    client.subscribe("wagen")

    # LED Tuer Thread starten
    tuer_thread = threading.Thread(target=tuer_thread)

    # LED Wagen Thread starten
    wagen_links_thread = threading.Thread(target=wagen_thread)
    wagen_rechts_thread = threading.Thread(target=wagen_thread)

    #LED refresh Thread starten
    neopixel_refresh_thread = threading.Thread(target=neopixel_thread, args=(strip,leds,))
    neopixel_refresh_thread.start()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        client.loop_forever()

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(leds, Color(0,0,0), 10)
            time.sleep(1)
