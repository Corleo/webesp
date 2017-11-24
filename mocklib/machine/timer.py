'''
https://github.com/micropython/micropython-lib/blob/master/machine/machine/timer.py
https://github.com/micropython/micropython/blob/master/unix/modffi.c#L101
http://man7.org/linux/man-pages/man2/timer_settime.2.html
'''

import os
import uos
import errno
import utime
import array
import ffilib
import uctypes
from signal import *

libc  = ffilib.libc()
librt = ffilib.open("librt")

_ONE_SHOT = const(0)
_PERIODIC = const(1)

_CLOCK_REALTIME  = const(0)
_CLOCK_MONOTONIC = const(1)
_SIGEV_SIGNAL    = const(0)

_MILISECOND = const(1000000)

sigval_t = {
    "sival_int": uctypes.INT32 | 0,
    "sival_ptr": (uctypes.PTR | 0, uctypes.UINT8),
}

sigevent_t = {
    "sigev_value": (0, sigval_t),
    "sigev_signo": uctypes.INT32 | 8,
    "sigev_notify": uctypes.INT32 | 12,
}

timespec_t = {
    "tv_sec": uctypes.INT32 | 0,
    "tv_nsec": uctypes.INT64 | 8,
}

itimerspec_t = {
    "it_interval": (0, timespec_t),
    "it_value": (16, timespec_t),
}

__libc_current_sigrtmin = libc.func("i", "__libc_current_sigrtmin", "")
SIGRTMIN = __libc_current_sigrtmin()

timer_create_  = librt.func("i", "timer_create", "ipp")
timer_delete_  = librt.func("i", "timer_delete", "p")
timer_settime_ = librt.func("i", "timer_settime", "PiPp")

def new(sdesc):
    buf = bytearray(uctypes.sizeof(sdesc))
    s = uctypes.struct(uctypes.addressof(buf), sdesc, uctypes.NATIVE)
    return s

def timer_create(sig_id):
    sev = new(sigevent_t)
    #print(sev)
    sev.sigev_notify = _SIGEV_SIGNAL
    sev.sigev_signo = SIGRTMIN + sig_id
    timerid = array.array('P', [0])
    r = timer_create_(_CLOCK_MONOTONIC, sev, timerid)
    os.check_error(r)
    # print("timerid", hex(timerid[0]))
    return timerid[0]

def timer_delete(tid):
    try:
        r = timer_delete_(tid)
        # print("timer_delete", r, uos.errno())
        os.check_error(r)
    except OSError:
        e = uos.errno()
        if e != errno.EINVAL:
            raise(e)

def timer_settime(tid, period, mode):
    """
    period in milisecond
    """
    period = _MILISECOND * period
    new_val = new(itimerspec_t)
    new_val.it_value.tv_nsec = period
    if mode == _PERIODIC:
        new_val.it_interval.tv_nsec = period
    #print("new_val:", bytes(new_val))
    old_val = new(itimerspec_t)
    #print("old_val:", bytes(old_val))
    #print(new_val, old_val)
    r = timer_settime_(tid, 0, new_val, old_val)
    os.check_error(r)
    #print("timer_settime", r)

def timer_disarm(tid):
    no_val = new(itimerspec_t)
    r = timer_settime_(tid, 0, no_val, no_val)
    os.check_error(r)
    # print("no_val:", bytes(no_val))
    # print("timer_disarm", r)


class Timer:
    ONE_SHOT = _ONE_SHOT
    PERIODIC = _PERIODIC

    def __init__(self, id=-1):
        self.tid       = None
        self._id       = None
        self._mode     = None
        self._period   = None
        self._callback = None

        self.id(id)

    def id(self, *arg):
        """
        Timer id value -1 is expected by the Esp for soft timer but the librt
        timer in unix don't allow negative ids.
        """
        if not arg:
            return self._id
        elif arg[0] != -1:
            raise ValueError("ValueError: not a valid Timer id: {}".format(arg[0]))
        else:
            self._id = arg[0] if arg[0] > 0 else 0

    def period(self, *arg):
        if not arg:
            return self._period
        elif not isinstance(arg[0], int):
            raise ValueError("ValueError: Timer period '{}' is not a integer value: {}".format(arg[0], type(arg[0])))
        elif arg[0] <= 0:
            raise ValueError("ValueError: Timer period '{}' is not a positive number".format(arg[0]))
        elif arg[0] > 999:
            raise ValueError("ValueError: Timer period '{}' is greater than 999 ms".format(arg[0]))
        else:
            self._period = arg[0]

    def mode(self, *arg):
        if not arg:
            return self._mode
        elif arg[0] != 0 and arg[0] != 1:
            raise ValueError("ValueError: not a valid Timer mode: {}".format(arg[0]))
        else:
            self._mode = arg[0]

    def callback(self, *arg):
        if not arg:
            return self._callback
        elif not callable(arg[0]):
            raise TypeError("TypeError: '{}' object is not callable".format(arg[0]))
        else:
            self._callback = arg[0]

    def init(self, period, mode, callback):
        self.tid = timer_create(self._id)
        self.period(period)
        self.mode(mode)
        self.callback(callback)

        timer_settime(self.tid, self._period, self._mode)
        org_sig = signal(SIGRTMIN + self._id, self.handler)
        #print("Sig {}: {}".format(SIGRTMIN + self._id, org_sig))

    def handler(self, signum):
        # print('Signal handler called with signal', signum)
        self._callback(self)

    def deinit(self):
        if self.tid is not None:
            timer_delete(self.tid)
