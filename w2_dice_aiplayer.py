from w2_dice_board import Row
from w2_dice_player_ga import CrossPossibility, Player
from typing import List
import numpy as np
import random


class AI(Player):
    def __init__(self, name, opponents, strategy, bias):
        super().__init__(name, opponents)
        self.linear_factor = strategy
        self.bias = bias

    def _get_sum_situation_(self, hypothetical_situation):
        situation_quality = 0
        for index in range(len(hypothetical_situation)):
            situation_quality += hypothetical_situation[index] * (self.linear_factor * (self.opponents + 1))[index] + \
                                 self.bias[index]  # todo: get rid off self_opponents
        return situation_quality

    def get_possibilities_active(self, lst_eyes) -> List[List[CrossPossibility]]:
        possibilities_white_white = []
        possibilities_white_color = []

        white_dice_sum = lst_eyes[0] + lst_eyes[1]
        for row in Row:  # weiße summe ankreuzen
            if row in (Row.RED, Row.YELLOW):
                if not self.completed_lines[row] and self.board.row_limits[row] < white_dice_sum and (
                        (self.board.row_numbers[row] >= 5 and white_dice_sum == 12) or white_dice_sum < 12):
                    possibilities_white_white.append([CrossPossibility(row, white_dice_sum)])
            else:
                if not self.completed_lines[row] and self.board.row_limits[row] > white_dice_sum and (
                        (self.board.row_numbers[row] >= 5 and white_dice_sum == 2) or white_dice_sum > 2):
                    possibilities_white_white.append([CrossPossibility(row, white_dice_sum)])
        possibility_lst = possibilities_white_white.copy()

        for color in Row:  # weiß + farbe
            for white in range(2):
                white_color_sum = lst_eyes[white] + lst_eyes[color + 2]
                if color in (Row.RED, Row.YELLOW):
                    if not self.completed_lines[color] and self.board.row_limits[color] < white_color_sum and (
                            (self.board.row_numbers[color] >= 5 and white_color_sum == 12) or white_color_sum < 12):
                        possibilities_white_color.append([CrossPossibility(color, white_color_sum)])
                else:
                    if not self.completed_lines[color] and self.board.row_limits[color] > white_color_sum and (
                            (self.board.row_numbers[color] >= 5 and white_color_sum == 2) or white_color_sum > 2):
                        possibilities_white_color.append([CrossPossibility(color, white_color_sum)])
        possibility_lst.extend(possibilities_white_color)

        for white_white in possibilities_white_white:
            white_white = white_white[0]
            for white_color in possibilities_white_color:
                white_color = white_color[0]
                if (white_white.row != white_color.row) or (
                        white_white.row in (Row.RED, Row.YELLOW) and white_white.eyes < white_color.eyes) or (
                        white_white.row in (Row.GREEN, Row.BLUE) and white_white.eyes > white_color.eyes):
                    possibility_lst.append([white_white, white_color])

        assert(self.board.penalties < 4)
        possibility_lst.append([CrossPossibility(4, 1)])
        return possibility_lst

    def _find_best_turns(self, possibilities, is_active_player) -> List[CrossPossibility]:
        # return possibilities[-1]
        max_turns_strength = -1000
        best_turns = None
        for possibility in possibilities:
            turns_strength = self._get_sum_situation_(self._get_situation_(is_active_player, possibility))
            if turns_strength > max_turns_strength:
                best_turns = possibility
                max_turns_strength = turns_strength
        return best_turns

    def cross_active(self, lst_eyes) -> List[CrossPossibility]:
        possibilities = self.get_possibilities_active(lst_eyes)
        return self._find_best_turns(possibilities, True)

    def get_possibilities_passive(self, lst_eyes) -> List[List[CrossPossibility]]:
        possibility_lst = []
        white_dice_sum = lst_eyes[0] + lst_eyes[1]
        for row in Row:
            if row in (Row.RED, Row.YELLOW):
                if not self.completed_lines[row] and self.board.row_limits[row] < white_dice_sum and (
                        (self.board.row_numbers[row] >= 5 and white_dice_sum == 12) or white_dice_sum < 12):
                    possibility_lst.append([CrossPossibility(row, white_dice_sum)])
            else:
                if not self.completed_lines[row] and self.board.row_limits[row] > white_dice_sum and (
                        (self.board.row_numbers[row] >= 5 and white_dice_sum == 2) or white_dice_sum > 2):
                    possibility_lst.append([CrossPossibility(row, white_dice_sum)])

        assert (self.board.penalties < 4)
        possibility_lst.append([CrossPossibility(4, 1)])
        possibility_lst.append([CrossPossibility(None, None)])
        return possibility_lst

    def cross_passive(self, lst_eyes):
        possibilities = self.get_possibilities_passive(lst_eyes)
        return self._find_best_turns(possibilities, False)
