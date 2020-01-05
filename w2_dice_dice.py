from random import randint


class Dice:
    def __init__(self, sides=6):
        self.sides = sides

    def throw(self):
        lst_eyes = []
        for i in range(6):             # 6 dice in game qwixx
            lst_eyes.append(randint(1, 6))
        return lst_eyes
        # return [3, 4, 1, 1, 1, 1]


dice = Dice


def test():
    dice.throw(dice)
    print("expected result: ")
    print("")
    print("-----------------------------------------------------------------------------------------------------------")
    print(dice.lst_eyes)
    print("expected result: ")
    print("(array with 6 numbers between 1 and 6)")
    print("-----------------------------------------------------------------------------------------------------------")
    dice.throw(dice)
    print(dice.lst_eyes)
    dice.throw(dice)
    print(dice.lst_eyes)
    dice.throw(dice)
    print(dice.lst_eyes)
    print("expected result: ")
    print("(3 (probably) different arrays with 6 numbers between 1 and 6)")
    print("-----------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
    test()