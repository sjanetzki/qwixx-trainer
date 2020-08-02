"""This file creates the board of Qwixx, sets valid crosses and calculates the total points."""
import numpy as np
from enum import IntEnum


class Row(IntEnum):
    """gives colors of the rows a number"""
    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3


class Board:
    """does everything that happens on the board"""
    def __init__(self):
        self.penalties = 0
        self.crosses_by_color = [set(), set(), set(), set()]

    @property
    def row_limits(self):
        """finds the row limit of each line, which is the number on the furthest right"""
        row_limits = np.array([1, 1, 13, 13])
        for color, crosses in enumerate(self.crosses_by_color):
            if len(crosses) == 0:
                continue
            if color in (Row.RED, Row.YELLOW):
                row_limits[color] = max(crosses)
            else:
                row_limits[color] = min(crosses)
        return row_limits

    def _set_row_limits(self, row, value):
        """adds a new row limit (new cross)"""
        self.crosses_by_color[row].add(value)

    @property
    def row_numbers(self):
        """finds the number of crosses made in each line"""
        row_numbers = np.array([0, 0, 0, 0])
        for color, crosses in enumerate(self.crosses_by_color):
            row_numbers[color] = len(crosses)
        return row_numbers

    def show(self) -> None:
        """prints the board as a string"""
        row = [0, 1, 2, 3]

        row[0] = [" 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "11", "12", " 0"]
        row[1] = [" 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "11", "12", " 0"]
        row[2] = ["12", "11", "10", " 9", " 8", " 7", " 6", " 5", " 4", " 3", " 2", " 0"]
        row[3] = ["12", "11", "10", " 9", " 8", " 7", " 6", " 5", " 4", " 3", " 2", " 0"]

        join_r = ' '.join(row[0])
        join_y = ' '.join(row[1])
        join_g = ' '.join(row[2])
        join_b = ' '.join(row[3])
        print("red:    {}".format(join_r))
        print("yellow: {}".format(join_y))
        print("green:  {}".format(join_g))
        print("blue:   {}".format(join_b))
        if self.penalties == 0:
            print("penalties: 0")
        else:
            print("penalties: {}".format(self.penalties))

    def cross(self, position, completed_lines, is_active_player) -> bool:
        """sets the crosses chosen by the player after checking their validity, returns True if the turn is valid"""
        row = position.row
        eyes = position.eyes
        if row is None:
            if is_active_player:
                return False
            else:
                return True
        if row not in range(5):
            return False
        if row == 4:
            if self.penalties < 4:
                self.penalties += 1
                return True
            else:
                return False
        return self._make_colored_cross(eyes, row, completed_lines)

    def _make_colored_cross(self, eyes, row, completed_lines):
        """make cross in a colored row"""
        if eyes not in range(2, 13):
            return False
        if completed_lines[row]:  # row closed -> no crosses can be made there anymore
            print(completed_lines)
            print(row)
            print(self.row_limits)
            return False

        if row in (Row.RED, Row.YELLOW):
            cross_last_number = eyes == 12
        else:
            cross_last_number = eyes == 2

        if self.row_numbers[row] < 5 and cross_last_number:
            return False

        if row in (Row.RED, Row.YELLOW) and self.row_limits[row] < eyes:
            self._set_row_limits(row, eyes)
            if cross_last_number:
                self._set_row_limits(row, 13)
            return True
        elif row in (Row.GREEN, Row.BLUE) and self.row_limits[row] > eyes:
            self._set_row_limits(row, eyes)
            if cross_last_number:
                self._set_row_limits(row, 1)
            return True
        else:
            return False
