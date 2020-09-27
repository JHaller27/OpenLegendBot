from dice import *


class ActionDice:
    ATTRIBUTE_DICE_MAP = [
        (1, 4),
        (1, 6),
        (1, 8),
        (1, 10),
        (2, 6),
        (2, 8),
        (2, 10),
        (3, 8),
        (3, 10),
        (4, 8)
    ]

    def __init__(self, score):
        self._score = score
        self._dice = ActionDice.attribute_to_dice(score)

    def __repr__(self):
        return f"Attribute Score: {self._score}\n{str(self._dice)}"

    @staticmethod
    def attribute_to_dice(score):
        dice = Dice(1, 20)

        # Dice always explode
        dice.set_explode(True)

        if score <= 0:
            return dice

        if score - 1 >= len(ActionDice.ATTRIBUTE_DICE_MAP):
            raise ValueError(f"Invalid Attribute Score '{ascorettribute_score}'. Must be <= {len(ActionDice.ATTRIBUTE_DICE_MAP)}")

        dice_args = ActionDice.ATTRIBUTE_DICE_MAP[score - 1]

        dice += Dice(*dice_args)

        # Dice always explode
        dice.set_explode(True)

        return dice

    def advantage(self, num):
        assert num > 0, f"Cannot grant Advantage '{num}'"

        size = ActionDice.ATTRIBUTE_DICE_MAP[self._score - 1][1]
        self._dice %= Dice(num, size)
        self._dice[size] <<= num

    def disadvantage(self, num):
        assert num > 0, f"Cannot grant Disadvantage '{num}'"

        size = ActionDice.ATTRIBUTE_DICE_MAP[self._score - 1][1]
        self._dice %= Dice(num, size)
        self._dice[size] >>= num

    def legend(self, num):
        assert num > 0, f"Cannot spend '{num}' Legend Points"

        self.advantage(num)
        self._dice += num

    def roll(self):
        return self._dice.get_result()


if __name__ == "__main__":
    roller = ActionDice(5)
    roller.advantage(1)
    roller.legend(2)

    print(roller)
    print()

    roller.roll()
    print(roller)
