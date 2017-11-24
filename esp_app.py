"""
Unix / Esp micropython app.

Unix exec:
    $ upython esp_app.py
    $ upython esp_app.py foo

Tests:
    $ mqttp 'period/mqttDev1' -m '{"ctrl_id":"wNYO4vfP1rh61HAc","period":"1000"}'

    $ mqttp 'devicectrl/mqttDev1' -m '{"ctrl_id":"wNYO4vfP1rh61HAc","command":"toggle"}'
    $ mqttp 'devicectrl/mqttDev1' -m '{"ctrl_id":"wNYO4vfP1rh61HAc","command":"conn"}'
    $ mqttp 'devicectrl/mqttDev1' -m '{"ctrl_id":"wNYO4vfP1rh61HAc","command":"disc"}'

    $ mqttp 'devicectrlcb/mqttDev1' -m 'successfully_connected'

    $ mqtts 'measure/mqttDev1'
    $ mqtts 'devicectrlcb/mqttDev1'
    $ mqtts 'calibration/mqttDev1'
"""


try:
    # print('PROD_IMPORT')

    import network
    import machine
    import ubinascii
except:
    print('DEV_IMPORT')

    import sys
    import mocklib.machine as machine


import ujson
import utime
import webapp_cfg
from array import array
import umqtt.simple as umqtt
# import umqtt.robust as umqtt

import gc
gc.collect()
# gc.threshold((gc.mem_free() + gc.mem_alloc()) // 2)
# gc.threshold(gc.mem_free() // 3 + gc.mem_alloc())
# gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
# gc.threshold(3072 + gc.mem_alloc())

# ''' FOR_DEBUG
print("Garbage collect free: {} allocated: {}".format(gc.mem_free(), gc.mem_alloc()))
print("Collector enabled: {}".format(gc.isenabled()))
print("Garbage threshold: {}".format(gc.threshold()))
# '''

# GLOBALS
_BUFFERSIZE = const(80)
measures    = array('l', 0 for x in range(_BUFFERSIZE))
index       = 0

period      = 5
toggle      = False
dev_ctrl_id = None
web_ctrl_id = None

try:
    # print('PROD_INIT')

    sta_if    = network.WLAN(network.STA_IF)
    dev_id    = ubinascii.hexlify(sta_if.config("mac"))
    adc_read2 = machine.ADC(0).read
except:
    print('DEV_INIT')

    try:    dev_id = (sys.argv[1]).encode()
    except: dev_id = b'mqttDev1'

    adc_read2 = machine.ADC(0).read2

client   = None # mqtt client object
timer    = machine.Timer(-1)
adc_read = machine.ADC(0).read


# sub topics
t_period   = "period/{:s}".format(dev_id).encode()
t_dev_ctrl = "devicectrl/{:s}".format(dev_id).encode()

# pub topics
t_measure     = "measure/{:s}".format(dev_id).encode()
t_dev_ctrl_cb = "devicectrlcb/{:s}".format(dev_id).encode()
t_calibration = "calibration/{:s}".format(dev_id).encode()

''' FOR_DEBUG
print("Setting topics:")
topics = [t_period, t_dev_ctrl, t_measure, t_dev_ctrl_cb, t_calibration]
for topic in topics:
    print(" * {:s}".format(topic))
print(" ")
# '''


def get_measure(t):
    global measures, index

    if index > _BUFFERSIZE:
        index = 0

    measures[index] = utime.ticks_us()
    index += 1
    measures[index] = adc_read()
    index += 1

    if index == _BUFFERSIZE:
        client.publish(t_measure, ujson.dumps(measures), False, 0)
        index = 0

        # print(measures)
        gc.collect()


def sub_cb(topic, msg):
    global dev_ctrl_id, web_ctrl_id, period, toggle, measures, index, timer, client

    payload = ujson.loads(msg)
    web_ctrl_id = str(payload['ctrl_id'])

    # Connection, calibration and toggle measurement controller
    if topic == t_dev_ctrl:
        command = str(payload['command'])

        if dev_ctrl_id is None and web_ctrl_id is not None:
            if command == "conn":
                dev_ctrl_id = web_ctrl_id
                client.publish(t_dev_ctrl_cb, 'successfully_connected', False, 1)

        elif dev_ctrl_id == web_ctrl_id:
            if command == "conn":
                client.publish(t_dev_ctrl_cb, 'already_connected', False, 1)

            elif command == "disc":
                timer.deinit()
                index       = 0
                toggle      = False
                dev_ctrl_id = None
                client.publish(t_dev_ctrl_cb, 'successfully_disconnected', False, 1)

            elif command == "unsub":
                timer.deinit()
                index       = 0
                toggle      = False
                dev_ctrl_id = None
                client.publish(t_dev_ctrl_cb, 'ok_to_unsubscribe', False, 1)

            elif command == "toggle":
                toggle = not toggle

                if toggle:
                    timer.init(period=period, mode=machine.Timer.PERIODIC, callback=get_measure)
                else:
                    timer.deinit()
                    index = 0

            elif command == "calibrate":
                payload = '{{"voltage": {:d}}}'.format(adc_read2())

                client.publish(t_calibration, payload, False, 0)

        else:
            client.publish(t_dev_ctrl_cb, 'no_control_allowed', False, 1)

    # Period controller
    elif topic == t_period:
        if dev_ctrl_id is not None and dev_ctrl_id == web_ctrl_id:
            period = int(payload['period'])

        else:
            client.publish(t_dev_ctrl_cb, 'no_control_allowed', False, 1)

    gc.collect()
    print("topic: {} | msg: {}".format(topic, msg)) # FOR_DEBUG


def main(server=webapp_cfg.MQTT_SERVER, port=webapp_cfg.MQTT_PORT):
    global client, timer

    client = umqtt.MQTTClient(dev_id, server, port)
    client.set_callback(sub_cb)
    while client.connect(clean_session=True): utime.sleep_ms(500)
    client.subscribe(t_dev_ctrl, 1)
    client.subscribe(t_period, 1)
    client.publish(t_dev_ctrl_cb, 'esp_init', False, 1)
    print("New MQTT session at device {}".format(dev_id))

    gc.collect()

    try:
        while 1:
            if not toggle or utime.ticks_diff(utime.ticks_ms(), start) > 1000:
                try: client.check_msg()   # umqtt.simple
                # try: client.wait_msg()    # umqtt.robust

                except umqtt.MQTTException as e: print("MQTTException: {}".format(e))

                else:    start = utime.ticks_ms()
                finally: gc.collect()

            if not toggle: utime.sleep_ms(200)

    finally:
        print("\nDisconnecting MQTT client...")
        timer.deinit()
        client.publish(t_dev_ctrl_cb, 'esp_interrupted', False, 1)
        client.disconnect()
        print("MQTT client Disconnected!")
        gc.collect()


if __name__ == "__main__":
    main("localhost")
