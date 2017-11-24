import utime
import urandom

def rand_seed(seed):
    # for these choice of numbers, see P L'Ecuyer, "Tables of linear
    # congruential generators of different sizes and good lattice structure"
    urandom.seed((seed * 653276) % 8388593)


class ADC:
    CALIBER = const(6)

    def __init__(self, ch=0):
        self.ch(ch)
        self._value = None
        rand_seed(utime.ticks_us())

    def ch(self, *arg):
        if not arg:
            return self._ch
        elif arg[0] != 0 and arg[0] != 1:
            raise ValueError("ValueError: not a valid ADC channel: {}".format(arg[0]))
        else:
            self._ch = arg[0]

    def read(self, bits=10):
        utime.sleep_us(urandom.getrandbits(9))

        if bits == self.CALIBER:
            if not self._value:
                self._value = urandom.getrandbits(self.CALIBER)
            else:
                self._value += urandom.getrandbits(self.CALIBER)
        else:
            self._value = urandom.getrandbits(bits)

        return self._value

    def read2(self):
        return self.read(6)
