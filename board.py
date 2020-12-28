"""This file creates the board of Qwixx and sets valid crosses"""
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
        self.crosses_by_color = [set(), set(), set(), set()]        # Instanzvariabeln

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

    def _set_row_limits(self, row, value) -> None:
        """adds a new row limit (new cross)"""
        self.crosses_by_color[row].add(value)

    @property
    def row_numbers(self):
        """finds the number of crosses made in each line"""
        row_numbers = np.array([0, 0, 0, 0])
        for color, crosses in enumerate(self.crosses_by_color):
            row_numbers[color] = len(crosses)
        return row_numbers

    def cross(self, position, completed_lines, is_active_player) -> None:
        """sets the crosses chosen by the player after checking their validity"""
        row = position.row
        eyes = position.eyes
        if row is None:
            assert(not is_active_player)
            return
        assert(row in range(5))
        if row == 4:
            assert(self.penalties < 4)
            if self.penalties < 4:
                self.penalties += 1
                return
        self._make_colored_cross(eyes, row, completed_lines)

    def _make_colored_cross(self, eyes, row, completed_lines) -> None:
        """make cross in a colored row"""
        assert (eyes in range(2, 13))
        if completed_lines[row]:
            assert (not completed_lines[row])    # row closed -> no crosses can be made there anymore
        if row in (Row.RED, Row.YELLOW):
            cross_last_number = eyes == 12
        else:
            cross_last_number = eyes == 2
        assert (not (self.row_numbers[row] < 5 and cross_last_number))
        if row in (Row.RED, Row.YELLOW) and self.row_limits[row] < eyes:
            self._set_row_limits(row, eyes)
            if cross_last_number:
                self._set_row_limits(row, 13)
        elif row in (Row.GREEN, Row.BLUE) and self.row_limits[row] > eyes:
            self._set_row_limits(row, eyes)
            if cross_last_number:
                self._set_row_limits(row, 1)
        else:
            assert False
