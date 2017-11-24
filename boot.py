try:    import micropython
except: import mocklib.micropython as micropython

micropython.alloc_emergency_exception_buf(300)


def set_ap():
    import network
    import ubinascii
    import webapp_cfg

    # network.phy_mode(network.MODE_11G)
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    essid = "uPy-{:s}".format(ubinascii.hexlify(ap_if.config("mac")[-3:])).encode()
    ap_if.config(
        essid=essid,
        authmode=network.AUTH_WPA2_PSK,
        password=webapp_cfg.AP_PASS
    )


def set_sta(ssid='mosquito'):
    import utime
    import network

    # network.phy_mode(network.MODE_11G)
    network.WLAN(network.AP_IF).active(False)

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if not sta_if.isconnected():
        print('connecting to network...')

        scan  = sta_if.scan()  # (ssid, bssid, channel, RSSI, authmode, hidden)
        STAs  = [x[0].decode() for x in scan]
        SSIDs = {}

        with open('wifi_sta') as f:
            for i, val in enumerate(f):
                if i % 2 == 0:
                    key = val.replace('\n','')
                else:
                    SSIDs[key] = val.replace('\n','')

        if ssid in SSIDs.keys() and ssid in STAs:
            conn_2_sta(ssid, SSIDs[ssid], sta_if)
        else:
            for ssid in SSIDs.keys():
                if ssid in STAs:
                    if conn_2_sta(ssid, SSIDs[ssid], sta_if):
                        return True

        if not sta_if.isconnected():
            sta_if.disconnect()
            return False

        return True


def conn_2_sta(ssid, password, sta_if):
    import utime

    start = utime.ticks_ms()
    sta_if.connect(ssid, password)

    while not sta_if.isconnected() and utime.ticks_diff(utime.ticks_ms(), start) < 10000:
            utime.sleep_ms(100)

    if sta_if.isconnected():
        return True
    else:
        return False


def new_sta(webrepl):
    import os
    import utime
    import network
    import machine

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    SSIDs      = []
    ssid       = input("new SSID: ")
    password   = input("password: ")
    reboot     = ""
    disconnect = ""

    with open("wifi_sta") as old_f:
        for l in old_f:
            SSIDs.append(l)

    if not "{}\n".format(ssid) in SSIDs:
        if conn_2_sta(ssid, password, sta_if):
            with open("wifi_sta.tmp", "wb") as new_f:
                SSIDs.append("{}\n".format(ssid))
                SSIDs.append("{}\n".format(password))

                for l in SSIDs[-10:]:
                    new_f.write(l)

            os.remove("wifi_sta")
            os.rename("wifi_sta.tmp", "wifi_sta")

            print("Success to connect to the new SSID '{}'!\n"
                "Keep in mind that only the last 5 SSIDs credentials are kept saved on this device.\n".format(ssid))

            while 1:
                reboot = input("Reboot to start the system? (y/n): ")
                if reboot in ("y", "n", ""): break

            if reboot == "y":
                print("The system will be rebooted in 10s.")
                webrepl.stop()

                network.WLAN(network.AP_IF).active(False)
                utime.sleep(10)

                machine.reset()
        else:
            print("Couldn't connect to '{}' SSID. Try again.".format(ssid))

        while 1:
            disconnect = input("Disconnect the webrepl? (y/n): ")
            if disconnect in ("y", "n", ""): break

        if disconnect == "y":
            webrepl.stop()
    else:
        return("The '{}' SSID is already registered on this device.".format(ssid))


if __name__ == '__main__':
    import gc
    gc.collect()

    import sys
    import esp
    import machine

    machine.freq(160000000)

    print("Performing initial setup...")
    if not set_sta():
        import webrepl
        set_ap()
        webrepl.start()

    esp.osdebug(None)
    gc.collect()

    del micropython
    del set_ap
    del set_sta
    del conn_2_sta
    del new_sta
    del machine
    del esp

    if 'bdev' in globals(): del bdev
    if 'uos' in globals(): del uos
    sys.modules.clear()
    del sys

    gc.collect()
    del gc
