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


class ThreadKillable:
    def __init__(self, target, args=()):
        self.exit_request = False
        self.started = False
        self.thread = threading.Thread(target=target,args=(self,)+args)
    def start(self):
        self.thread.start()
        self.started = True
    def stop(self):
        self.exit_request = True
        if self.started:
            self.thread.join()
    

class LED:
    def __init__(self, color):
        self.color = color
        
    def set_color(self, color):
        self.color = color
        
#-------------------------------------------------
# Threads

# LED Wagen Thread starten
#wagen_links_thread = ThreadKillable()
#wagen_rechts_thread = ThreadKillable()
#tuer_thread = ThreadKillable()

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
    global tuer_thread
    global wagen_rechts_thread
    global wagen_links_thread

    # Nachricht empfangen und als JSON-Dictionary decodieren
    msg = json.loads(message.payload.decode())
     # Überprüfe, von welchem Topic die Nachricht stammt
    if message.topic == "tuer":
        #den aktuellen tuer Thread beenden und neu starten

        tuer_thread.stop()
        tuer_thread =  ThreadKillable(target=tuer_programm,args=(tuer_links, tuer_rechts, msg,))
        tuer_thread.start()
    elif message.topic == "wagen":
         #den aktuellen tuer Thread beenden und neu starten
        wagen_rechts_thread.stop()
        wagen_links_thread.stop()
        wagen_rechts_thread = ThreadKillable(target=wagen_programm,args=(wagen_rechts,msg,))
        wagen_links_thread = ThreadKillable(target=wagen_programm,args=(wagen_links,msg,))
        wagen_rechts_thread.start()
        wagen_links_thread.start()
    else:
        # Keine passende Verarbeitung gefunden
        print("Unbekanntes Topic empfangen:", message.topic)

#-------------------------------------------------
#             Animations Thread

def wagen_programm(calling_thread, leds, msg):
    # Farbwerte aus dem Dictionary extrahieren
    r, g, b = msg.get("color",[255,255,255])
    color_arrays = msg.get("colors",[[255,255,255]])
    colors = [Color(*c) for c in color_arrays] 
    color=Color(r,g,b)
    # Programmart extrahieren
    prog = msg.get("program","notSpecified")

    if prog == "colorWipe":
        print ('Color wipe')
        while True:
            colorWipe(calling_thread, leds, colors)
            if calling_thread.exit_request:
                return

    elif prog == "theaterChase":
        print ('Theater Chase.')
        while True:
            theaterChase(calling_thread, leds, color)
            if calling_thread.exit_request:
                return

    elif prog == "rainbow":
        print ('Rainbow')
        while True:
            rainbow(calling_thread, leds)
            if calling_thread.exit_request:
                return
        
    elif prog == "rainbowCycle":
        print ("Rainbow Cycle")
        while True:
            rainbowCycle(calling_thread, leds)
            if calling_thread.exit_request:
                return

    elif prog == "theaterChaseRainbow":
        print ("Theater Chase Rainbow")
        while True:
            theaterChaseRainbow(calling_thread, leds)
            if calling_thread.exit_request:
                return
    else:
        print ("Program unknown - Color only")
        setColor(calling_thread, leds,color)
        if calling_thread.exit_request:
            return

def tuer_programm(calling_thread, leds_links, leds_rechts, msg):
    # Farbwerte aus dem Dictionary extrahieren
    r, g, b = msg.get("color",[0,0,0])
    color=Color(r,g,b)
    # Programmart extrahieren
    prog = msg.get("program","notSpecified")
    wait_ms = msg.get("waitInMs",50)
    reverse = msg.get("reverse",False)

    if prog == "flashing":
        print ("Flashing")
        flashing(calling_thread, leds_links + leds_rechts,color,wait_ms)
        if calling_thread.exit_request:
            return
    elif prog == "runningSimultaniously":
        print ("running simultaniously")
        running_simultaniously(calling_thread, leds_links, leds_rechts, color, wait_ms, reverse)
        if calling_thread.exit_request:
            return
    else:
        print ("Program unknown - Color only")
        setColor(calling_thread, leds_links + leds_rechts, color)
        if calling_thread.exit_request:
            return

#-------------------------------------------------
#             Meine Animationen

def running(exit_request, leds, color, wait_ms=50, gap=0, light=3):
    while True:
        for i in range(len(leds) - light - gap + 1):
            for j in range(i, i + light):
                leds[j].set_color(color)
            for k in range(i + light + gap, len(leds)):
                leds[k].set_color(Color(0, 0, 0))
            if calling_thread.exit_request:
                return
            else:
                time.sleep(wait_ms / 1000.0)

#def running_simultaniously (leds1, leds2, color, wait_ms, gap, light):
#  n = min(len(leds1), len(leds2))
#  while True:
#    for i in range(n - light - gap + 1):
#      for j in range(i, i + light):
#        leds1[j].set_color(color)
#        leds2[j].set_color(color)
#      for k in range(i + light + gap, n):
#        leds1[k].set_color(Color(0, 0, 0))
#        leds2[k].set_color(Color(0, 0, 0))
#      time.sleep(wait_ms / 1000.0)

def running_simultaniously (calling_thread, leds1, leds2, color, wait_ms=50, reverse=False, gap=3, light=3):
  n = min(len(leds1), len(leds2))
  while True:
    for i in range(n - light - gap + 1):
        if reverse:
            i = n - light - gap - i
        for j in range(i, i + light):
            leds1[j].set_color(color)
            leds2[j].set_color(color)
        for k in range(i + light + gap, n):
            leds1[k].set_color(Color(0, 0, 0))
            leds2[k].set_color(Color(0, 0, 0))
        if calling_thread.exit_request:
            return
        else:
            time.sleep(wait_ms / 1000.0)  

def setColor(calling_thread, leds, color):
    while True:
        # Farbwerte ausgeben
        for led in leds:
            led.set_color(color)
        # Exit animation
        if calling_thread.exit_request:
            return
        else:
            time.sleep(0.5)

def flashing(calling_thread, leds, color, wait_ms=50, wait_off_ms=50):
    while True:
        # Farbwerte ausgeben
        for led in leds:
            led.set_color(color)
        # Exit animation
        if calling_thread.exit_request:
            return
        else:
            time.sleep(wait_ms/1000.0)
        # LED ausschalten
        for led in leds:
            led.set_color(Color(0,0,0))
        # Exit animation
        if calling_thread.exit_request:
            return
        else:
            time.sleep(wait_off_ms/1000.0)

#-------------------------------------------------
#           Beispiel Animationen

# Define functions which animate LEDs in various ways.
def colorWipe(calling_thread, leds, colors, wait_ms=25):
    """Wipe color across display a pixel at a time."""
    for led in leds:
        led.color = Color(0,0,0)
    for color in colors:
        for led in leds:
            led.color = color
            # Exit animation
            if calling_thread.exit_request:
                return
            else:
                time.sleep(wait_ms/1000.0)

def theaterChase(calling_thread, leds, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(color)            
            # Exit animation
            if calling_thread.exit_request:
                return
            else:
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

def rainbow(calling_thread, leds, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(len(leds)):
            leds[i].set_color(wheel((i+j) & 255))
        # Exit animation
        if calling_thread.exit_request:
            return
        else:
            time.sleep(wait_ms/1000.0)

def rainbowCycle(calling_thread, leds, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(len(leds)):
            leds[i].set_color(wheel(min(255,(int(i * 256 / len(leds)) + j) & 255)))
        # Exit animation
        if calling_thread.exit_request:
            return
        else:
            time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(calling_thread, leds, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, len(leds), 3):
                leds[(i+q)%(len(leds)-1)].set_color(wheel((i+j) % 255))
            # Exit animation
            if calling_thread.exit_request:
                return
            else:
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
        wagen_links.append(leds[i])
    wagen_rechts=[]
    for i in range(413,192,-1):
        wagen_rechts.append(leds[i])

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
    print ("Subscribe topic 'tuer'")
    client.subscribe("tuer")
    print ("Subscribe topic 'wagen'")
    client.subscribe("wagen")

    # LED Tuer Thread starten
    tuer_thread = ThreadKillable(tuer_programm)

    # LED Wagen Thread starten
    wagen_links_thread = ThreadKillable(wagen_programm)
    wagen_rechts_thread = ThreadKillable(wagen_programm)

    #LED refresh Thread starten
    neopixel_refresh_thread = threading.Thread(target=neopixel_thread,args=(strip,leds,))
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
