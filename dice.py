from random import randint


class Dice:
    """throws dice"""
    def __init__(self, sides=6):
        self.sides = sides

    def throw(self):
        """creates a random list of eyes of 6 dice"""
        lst_eyes = []
        for i in range(6):             # 6 dice in game qwixx
            lst_eyes.append(randint(1, 6))
        return lst_eyes
        # return [3, 4, 1, 1, 1, 1]

