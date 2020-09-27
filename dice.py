from random import randint


def round(x):
    if int(x*10) - (int(x) * 10) >= 5:
        return int(x) + 1
    else:
        return int(x)


class Dice:
    def __init__(self, num, size):
        self._num = num
        self._size = size
        self._explode = False
        self._mod = None
        self._result = None
        self._rolls = None
        self._ldrop = None
        self._rdrop = None
        self._ldrop_count = None
        self._rdrop_count = None

    def __repr__(self) -> str:
        s = self.get_dice_notation()

        if self._mod is not None:
            s += self.get_mod_notation()

        if self._rolls is not None:
            s += "\n" + self.get_rolls_notation()
            if self._mod is not None:
                s += self.get_mod_notation()

        if self._result is not None:
            s += "\n" + self.get_result_str()

        return s

    def __add__(self, other):
        if isinstance(other, Dice):
            return MultiDice([self, other])

        if not isinstance(other, int):
            raise NotImplementedError

        cp = self._copy()
        if cp._mod is None:
            cp._mod = 0
        cp._mod += other

        return cp

    def __iadd__(self, other):
        if isinstance(other, Dice):
            return MultiDice([self, other])

        if not isinstance(other, int):
            raise NotImplementedError

        if self._mod is None:
            self._mod = 0
        self._mod += other

        return self

    def __sub__(self, other):
        return self.__add__(-other)

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        cp = self._copy()
        cp._num *= other

        return cp

    def __imul__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        self._num *= other

        return self

    def __floordiv__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        cp = self._copy()
        cp._num //= other

        return cp

    def __ifloordiv__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        self._num //= other

        return self

    def __mod__(self, other):
        cp = self._copy()
        return cp.__imod__(other)

    def __imod__(self, other):
        if not isinstance(other, Dice):
            raise NotImplementedError

        if other._size != self._size:
            raise ValueError(f"Cannot add d{other._size}s to d{self._dize}s")

        self._num += other._num

        return self

    def __lshift__(self, other):
        cp = self._copy()
        return cp.__ilshift__(other)

    def __ilshift__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        self._ldrop_count = other

        if self._rolls is not None:
            if self._ldrop is None:
                self._ldrop = []
            self._ldrop = self._rolls[:other]
            self._rolls = self._rolls[other:]

        return self

    def __rshift__(self, other):
        cp = self._copy()
        return cp.__irshift__(other)

    def __irshift__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        self._rdrop_count = other

        if self._rolls is not None:
            if self._rdrop is None:
                self._rdrop = []
            self._rdrop = self._rolls[other:]
            self._rolls = self._rdrop

        return self

    def __neg__(self):
        return NegaDice(self._num, self._size)

    def __int__(self):
        return self.get_result()

    def __list__(self):
        return self._rolls

    def __lt__(self, other):
        if self._result is None:
            raise RuntimeError("Dice not rolled yet")

        if isinstance(other, Dice):
            if other._result is None:
                raise RuntimeError("Dice not rolled yet")

            return self._result < other._result

        if isinstance(other, int):
            return self._result < other

        raise NotImplementedError

    def __eq__(self, other):
        if self._result is None:
            raise RuntimeError("Dice not rolled yet")

        if isinstance(other, Dice):
            if other._result is None:
                raise RuntimeError("Dice not rolled yet")

            return self._result == other._result

        if isinstance(other, int):
            return self._result == other

        raise NotImplementedError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self._result is None:
            raise RuntimeError("Dice not rolled yet")

        if isinstance(other, Dice):
            if other._result is None:
                raise RuntimeError("Dice not rolled yet")

            return self._result > other._result

        if isinstance(other, int):
            return self._result > other

        raise NotImplementedError

    def __le__(self, other):
        try:
            return self.__eq__(other)
        except:
            return self.__lt__(other)

    def __ge__(self, other):
        try:
            return self.__eq__(other)
        except:
            return self.__gt__(other)

    def _copy(self):
        cp = Dice(self._num, self._size)
        cp._mod = self._mod
        cp._result = self._result
        cp._rolls = self._rolls

        return cp

    @classmethod
    def roll(cls, num, size):
        d = cls(num, size)
        d.get_result()
        return d

    def get_dice_notation(self) -> str:
        s = f"{self._num}d{self._size}"

        if self._ldrop_count is not None:
            s += f"dl{self._ldrop_count}"
        if self._rdrop_count is not None:
            s += f"dh{self._rdrop_count}"
        if self._explode:
            s += "e"

        return s

    def _get_dice_sep(self, first) -> str:
        return " + " if not first else ""

    def set_explode(self, explode=True):
        self._explode = explode

    def get_mod_notation(self) -> str:
        if self._mod >= 0:
            return f" + {self._mod}"
        else:
            return f" - {-self._mod}"

    def get_rolls_notation(self) -> str:
        ldrop_str = "<{}>".format(" + ".join(map(str, self._ldrop))) + " + " if self._ldrop is not None else ""
        keep_str = " + ".join(map(str, self._rolls))
        rdrop_str = "+ " + "<{}>".format(" + ".join(map(str, self._rdrop))) if self._rdrop is not None else ""

        return ldrop_str + keep_str + rdrop_str

    def get_result_str(self) -> str:
        return f"Result: {self._result}"

    def get_result(self):
        if self._result is None:
            # Base roll
            self._rolls = sorted([randint(1, self._size) for _ in range(self._num)])

            # Drop left/right
            if self._ldrop_count is not None:
                self._ldrop = self._rolls[:self._ldrop_count]
                self._rolls = self._rolls[self._ldrop_count:]
            if self._rdrop_count is not None:
                self._rdrop = self._rolls[self._ldrop_count:]
                self._rolls = self._rolls[:self._rdrop_count]

            # Explode
            if self._explode:
                for r in self._rolls:
                    if r == self._size:
                        self._rolls.append(randint(1, self._size))

            # Sum
            self._result = sum(self._rolls)

            # Modifier
            if self._mod is not None:
                self._result += self._mod

        return self._result

    def reset(self):
        self._mod = None
        self._result = None
        self._rolls = None
        self._ldrop = None
        self._rdrop = None
        self._ldrop_count = None
        self._rdrop_count = None

    def get_average(self, rnd=False):
        total = self._num * (self._size + 1) / 2

        if rnd:
            total = rount(total)

        return total


class NegaDice(Dice):
    def __neg__(self):
        return Dice(self._num, self._size)

    def get_result(self):
        if self._result is None:
            super().get_result()
            self._result = -self._result
        return self._result

    def _get_dice_sep(self, first) -> str:
        return " - "

    def get_average(self, rnd=False):
        return -super().get_average(rnd)


class MultiDice(Dice):
    def __init__(self, dice):
        if dice is None:
            self._dice = []
        elif isinstance(dice, Dice):
            self._dice = [dice]
        elif isinstance(dice, MultiDice):
            self._dice = dice._dice
        else:
            self._dice = list(dice)

        self._mod = None
        self._result = None

    def __repr__(self) -> str:
        s = ""

        # 1d20 + 4d6 - 1d8
        first = True
        for d in self._dice:
            s += d._get_dice_sep(first) + d.get_dice_notation()
            if first:
                first = False

        # + 5
        if self._mod is not None:
            s += self.get_mod_notation()

        # Actual rolls
        roll_strs = ""
        for d in self._dice:
            if d._rolls is not None:
                roll_strs += d._get_dice_sep(len(roll_strs) == 0) + "[{}]".format(d.get_rolls_notation())

        if len(roll_strs) > 0:
            s += "\n" + roll_strs
            if self._mod is not None:
                s += self.get_mod_notation()

        # Result
        if self._result is not None:
            s += "\n" + self.get_result_str()

        return s

    def __add__(self, other):
        cp = self._copy()
        return cp.__iadd__(other)

    def __iadd__(self, other):
        if isinstance(other, MultiDice):
            self._dice.extend(other._dice)

        elif isinstance(other, Dice):
            self._dice.append(other)

        elif isinstance(other, int):
            if self._mod is None:
                self._mod = 0
            self._mod += other

        else:
            raise NotImplementedError

        return self

    def __sub__(self, other):
        cp = self._copy()
        return self.__isub__(other)

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __mul__(self, other):
        cp = self._copy()
        return cp.__imul__(other)

    def __imul__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        for d in self._dice:
            d *= other

        return self

    def __floordiv__(self, other):
        cp = self._copy()
        return cp.__ifloordiv__(other)

    def __ifloordiv__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError

        for d in self._dice:
            d._num //= other

        return self

    def __mod__(self, other):
        cp = self._copy()
        return cp.__imod__(other)

    def __imod__(self, other):
        if isinstance(other, MultiDice):
            for d in other._dice:
                self %= d

        elif isinstance(other, Dice):
            for d in self._dice:
                if d._size == other._size:
                    d %= other
                    return self

        else:
            raise NotImplementedError

    def __neg__(self):
        return MultiDice(map(lambda d: -d, self._dice))

    def __int__(self):
        return self._result

    def __list__(self):
        return self._dice

    def __getitem__(self, size):
        for d in self._dice:
            if d._size == size:
                return d

    def __setitem__(self, size, dice):
        new = []

        for d in self._dice:
            if d._size != size:
                new.append(d)
            else:
                new.append(dice)

        self._dice = new

    def _copy(self):
        cp = MultiDice(self._dice)
        cp._mod = self._mod
        cp._result = self._result

        return cp

    @classmethod
    def roll(cls, *dice_tupes):
        md = MultiDice([Dice(num, size) for num, size in dice_tupes])
        md.get_result()

        return md

    def get_result(self):
        if self._result is None:
            self._result = 0
            for d in self._dice:
                self._result += d.get_result()

        if self._mod is not None:
            self._result += self._mod

        return self._result

    def set_explode(self, explode=True):
        for d in self._dice:
            d.set_explode(explode)

    def reset(self):
        for d in self._dice:
            d.reset()

        self._mod = None
        self._result = None

    def get_average(self, rnd=False):
        total = sum(map(lambda d: d.get_average(False), self._dice))

        if rnd:
            total = round(total)

        return total


if __name__ == "__main__":
    # Roll OpenLegend attribute
    d = Dice(1, 20)

    # Attribute Score 5 (2d6)
    d += Dice(2, 6)

    # Spent 2 Legend Points
    d %= Dice(2, 6)
    d[6] <<= 2
    d += 2

    # Set explode
    d.set_explode()

    # Roll & print
    d.get_result()
    print(d)

    # Get average
    avg = d.get_average(True)
    print(f"Average: {avg}")
