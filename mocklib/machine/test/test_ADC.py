from mocklib.machine import ADC


def test_adc_channel_numbers(_ch):
    print("test_adc_channel_numbers(_ch={}):".format(_ch))
    try:
        adc = ADC(_ch)
    except ValueError as e:
        print(e)
        print("NOT OK")
    else:
        print("OK")

    print()

def test_adc_default_channel():
    print("test_adc_default_channel():")
    adc = ADC()

    try:
        assert adc.ch() == 0
    except AssertionError as e:
        print("ADC channel #", adc.ch(), "is not default", e)
        print("NOT OK")
    else:
        print("OK")

    print()

def test_adc_read_method(*_bits):
    print("test_adc_read_method(*_bits={}):".format(_bits))
    adc = ADC()

    try:
        for i in range(10):
            reading = adc.read() if not _bits else adc.read(_bits[0])
            assert reading is not None
            print('i:', i, ' adc:', reading)
    except AssertionError as e:
        print("ADC read() method returns 'None'", e)
        print("NOT OK")
    else:
        print("OK")

    print()


if __name__ == "__main__":
    for i in range(4):
        test_adc_channel_numbers(i)


    test_adc_default_channel()


    test_adc_read_method()
    test_adc_read_method(10)
    test_adc_read_method(6)
