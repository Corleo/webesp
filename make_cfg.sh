#!/bin/bash

# run:
#   $ bash make_cfg.sh


# file: wifi_sta
# stores the ID and password of the wifi router in this order, with each
# one in a new line.
#
# Edit 'wifi_id' and 'wifi_pass' values.
wifi_id="put_wifi_id"
wifi_pass="put_wifi_password"

echo "$wifi_id" > wifi_sta
echo "$wifi_pass" >> wifi_sta


# file: webapp_cfg.py
# stores the password of the Esp8266 wifi access point and the mosquitto server
# and port address.
#
# Edit 'AP_PASS', 'MQTT_SERVER' and 'MQTT_PORT' values.
AP_PASS="esp_ap_password"
MQTT_SERVER="192.168.0.101"
MQTT_PORT=1883

echo "AP_PASS='$AP_PASS'" > webapp_cfg.py
echo "MQTT_SERVER='$MQTT_SERVER'" >> webapp_cfg.py
echo "MQTT_PORT=$MQTT_PORT" >> webapp_cfg.py


# file: webrepl_cfg.py
# stores the password of the webrepl to connecto to the Esp8266 REPL
#
# Edit 'PASS' value.
PASS='webrepl_password'

echo "PASS='$PASS'" > webrepl_cfg.py
