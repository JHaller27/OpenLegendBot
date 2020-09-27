from random import randint


class Dice:
    def __init__(self, num, size):
        self._num = num
        self._size = size
        self._mod = None
        self._result = None
        self._rolls = None

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

    def __neg__(self):
        return NegaDice(self._num, self._size)

    def __int__(self):
        return self._result

    def __list__(self):
        return self._rolls

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
        return f"{self._num}d{self._size}"

    def _get_dice_sep(self, first) -> str:
        return " + " if not first else ""

    def get_mod_notation(self) -> str:
        if self._mod >= 0:
            return f" + {self._mod}"
        else:
            return f" - {-self._mod}"

    def get_rolls_notation(self) -> str:
        return " + ".join(map(lambda r: f"{r}", self._rolls))

    def get_result_str(self) -> str:
        return f"Result: {self._result}"

    def get_result(self):
        if self._result is None:
            self._rolls = [randint(1, self._size) for _ in range(self._num)]
            self._result = sum(self._rolls)
        return self._result

    def reset(self):
        self._mod = None
        self._rolls = None
        self._result = None


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

    def __neg__(self):
        return MultiDice(map(lambda d: -d, self._dice))

    def __int__(self):
        return self._result

    def __list__(self):
        return self._dice

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

    def reset(self):
        for d in self._dice:
            d.reset()

        self._mod = None
        self._result = None


if __name__ == "__main__":
    a = Dice(1, 20) + Dice(1, 10)
    print(a)

    a = 5 + a
    print(a)

    print()
    a.get_result()
    print(a)
