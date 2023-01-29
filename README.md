# Faschingswagen

## MQTT Broker installieren
Herunterladen
> sudo apt install mosquitto mosquitto-clients

Autmatisch starten beim booten
```
sudo systemctl enable mosquitto
```
Die Datei für die Freigabe des Bokers im Netzwerk anpassen
```
sudo nano /etc/mosquitto/conf.d/local.conf
```
Folgende Zeilen werden in die Datei geschreiben
```
listener 1883<br>
allow_anonymous true
```
## MQTT Client für Python installieren

Herunterladen des MQTT Client mit
```
sudo pip install paho-mqtt
```
Importiere der Klasse mit
```
Import paho.mqtt.client as mqtt
```

Für Node Red ist keine MQTT Client Node zu installieren. Node Red liefert MQTT out-of-the-box

## ws_281x LED Adafruit Bibliothek installieren

Die ws281x LEDs müssen am GPIO 18 angeschlossen werden.

Die benötigten Packages installieren
```
sudo apt-get install gcc make build-essential python-dev git scons swigig
```
In folgender Datei muss das Audiointerface deaktiviert werden.
```
sudo nano /etc/modprobe.d/snd-blacklist.conf
```
Bitte die folgende Zeile ergänzen
```
blacklist snd_bcm2835
```
Ausserdem muss noch die Datei bearbeitet werden
```
sudo nano /boot/config.txt
```
```
# Enable audio (loads snd_bcm2835)
dtparam=audio=on
```
Das Reposetory mit der benötigten Bibliothek und mit Beispielanwendungen liegt hier
```
git clone https://github.com/rpi-ws281x/rpi-ws281x-python
```
Zu guter letzt müssen wir noch die Bibliothek installieren
```
sudo pip install rpi_ws281x
```
Importieren im Python Skript wie folgt
```
from rpi_ws281x import *
```