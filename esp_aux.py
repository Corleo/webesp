def keep_reading(time=2):
    # for calibration between ADC readings and the amplifier gain
    import utime
    import machine

    adc_read = machine.ADC(0).read
    while 1:
        try:
            print(adc_read())
            utime.sleep(time)
        except KeyboardInterrupt:  # Ctrl-C
            break


def dump_file(filename):
    with open(filename) as f:
        for l in f:
            print(l.replace("\n",''))


def disconnect_sta():
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
