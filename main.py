import sys

try:
    import network

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sys.exit("No wifi connection!")

    del sta_if
    del network
except:
    pass

import gc
import utime
import micropython
gc.disable()
gc.collect()

count = 1
while count <= 1:
    try:
        if 'esp_app' not in globals():
            import esp_app

        if 'webapp_cfg' not in globals():
            import webapp_cfg

        gc.collect()
        esp_app.main(webapp_cfg.MQTT_SERVER, webapp_cfg.MQTT_PORT)
    except KeyboardInterrupt:
        print("\nApp closed by keyboard interruption. Count #{}\n".format(count))
    except Exception as e:
        print("Exception #{}: {}".format(count, e))
        utime.sleep(1)
    finally:
        count += 1
        gc.collect()


gc.collect()
sys.modules.clear()
micropython.mem_info(1)

for item in ['esp_app', 'webapp_cfg', 'utime', 'count', 'micropython']:
    if item in globals(): del globals()[item]

del globals()['item']
del globals()['sys']

gc.enable()
gc.collect()
gc.collect()
gc.collect()

print("Garbage collect free: {} allocated: {}".format(gc.mem_free(), gc.mem_alloc()))
del globals()['gc']
