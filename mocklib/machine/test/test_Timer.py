from mocklib.machine import Timer
import utime


def test_timer_id(_id=None):
    print("test_timer_id(_id={}):".format(_id))
    try:
        timer = Timer(_id) if _id else Timer()
    except ValueError as e:
        print(e)
        print("NOT OK")
    else:
        print("timer.id:", timer._id)
        print("OK")

    print()

def test_timer_period(_period=None):
    print("test_timer_period(_period={}):".format(_period))
    timer = Timer()
    try:
        timer.period(_period)
    except ValueError as e:
        print(e)
        print("NOT OK")
    else:
        print("T_ms:", timer.period())
        print("OK")

    print()

def test_timer_mode(_mode=None):
    print("test_timer_mode(_mode={}):".format(_mode))
    timer = Timer()
    try:
        timer.mode(_mode)
    except ValueError as e:
        print(e)
        print("NOT OK")
    else:
        print("OK")

    print()

def test_timer_callback(_func=None):
    print("test_timer_callback(_func={}):".format(_func))
    timer = Timer()
    try:
        timer.callback(_func)
        timer._callback(timer)
    except TypeError as e:
        print(e)
        print("NOT OK")
    else:
        print("OK")

    print()

def test_timer_init(_period=None, _mode=None, _callback=None):
    print("test_timer_init(_period={}, _mode={}, _callback={}):".format(_period, _mode, _callback))

    global _f_init_index
    _f_init_index = 1

    timer = Timer()
    start = utime.ticks_us()
    count = 0
    try:
        timer.init(_period, _mode, _callback)
        while count < 10:
            utime.sleep_ms(_period)
            count += 1
            if not timer._mode: break
        timer.deinit()
    except OSError as e:
        print("OSError:", e)
        print("NOT OK")
    else:
        print("OK:", count, "x", timer._period, "ms ~", utime.ticks_diff(utime.ticks_us(), start), "us")

    print()

def test_timer_deinit(_period=None, _mode=None, _callback=None):
    print("test_timer_deinit(_period={}, _mode={}, _callback={}):".format(_period, _mode, _callback))

    global _f_deinit_index
    _f_deinit_index = 1

    timer = Timer()
    start = utime.ticks_us()
    count = 0
    try:
        timer.init(_period, _mode, _callback)
        while count < 10:
            utime.sleep_ms(_period)
            count += 1
            if _break: break
    except Exception as e:
        print(e)
        print("NOT OK")
    else:
        print("OK:", count, "x", timer._period, "ms ~", utime.ticks_diff(utime.ticks_us(), start), "us")

    print()


if __name__ == "__main__":
    # '''
    test_timer_id()
    test_timer_id(-1)
    test_timer_id(1)


    test_timer_period(100)
    test_timer_period(999)
    test_timer_period(1000)
    test_timer_period(1000.0)
    test_timer_period(-1)
    test_timer_period(0)
    test_timer_period()


    test_timer_mode(0)
    test_timer_mode(1)
    test_timer_mode(Timer.ONE_SHOT)
    test_timer_mode(Timer.PERIODIC)
    test_timer_mode(-1)
    test_timer_mode(2)
    test_timer_mode()


    def _f_callback(t): print('_func1, arg:', t)
    def _f_callback2(): print('_func2, no arg')
    test_timer_callback(_f_callback)
    test_timer_callback(_f_callback2)
    test_timer_callback(lambda t: print('lambda _func3, arg:', t))
    test_timer_callback('_func4')
    test_timer_callback(_f_callback(1))
    test_timer_callback()
    # '''


    # '''
    _f_init_index = 1
    def _f_init(t):
        global _f_init_index
        print("timer._mode:", t._mode, "| iter #", _f_init_index)
        _f_init_index += 1

    test_timer_init(999, Timer.PERIODIC, _f_init)
    test_timer_init(500, Timer.PERIODIC, _f_init)
    test_timer_init(500, Timer.ONE_SHOT, _f_init)
    test_timer_init(250, Timer.PERIODIC, _f_init)
    test_timer_init(500, Timer.ONE_SHOT, _f_init)
    # '''

    # '''
    _f_deinit_index = 1
    _break = False
    def _f_deinit(t):
        global _f_deinit_index, _break
        t.deinit()
        print("timer._mode:", t._mode, "| iter #", _f_deinit_index, "| timer:", t)
        _f_deinit_index += 1
        _break = True

    test_timer_deinit(500, Timer.ONE_SHOT, _f_deinit)
    test_timer_deinit(999, Timer.PERIODIC, _f_deinit)
    test_timer_deinit(250, Timer.PERIODIC, _f_deinit)
    # '''
