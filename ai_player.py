"""This file creates the 'brain' of an AI-player -> place of decision process what to do in the next turn"""
from board import Row
from player import CrossPossibility, Player
from typing import List
from time import sleep
import math


class AiPlayer(Player):     # todo add type annotations
    """an AI Player that decides on its own which crosses to make by evaluation;
    individual is characterized by its strategy"""

    def __init__(self, name, opponents, quadratic_factor, linear_factor, bias, ui=None):
        super().__init__(name, opponents, ui)
        self.quadratic_factor = quadratic_factor
        self.linear_factor = linear_factor
        self.bias = bias

    def _get_sum_situation_(self, hypothetical_situation) -> float:
        """evaluates the quality of a hypothetical situation that will be the situation after this turn"""
        situation_quality = 0
        for index in range(len(hypothetical_situation)):
            situation_quality += math.pow(hypothetical_situation[index], 2) * self.quadratic_factor[
                index % len(self.quadratic_factor)] + \
                                 hypothetical_situation[index] * self.linear_factor[index % len(self.linear_factor)] + \
                                 self.bias[index % len(self.bias)]  # todo: get rid off "%"
        return situation_quality

    def _get_possibilities_active(self, lst_eyes) -> List[List[CrossPossibility]]:
        """creates a list of all possible fields to make a cross on (while active player)"""
        possibilities_white_white = self._find_possible_white_white_sum(lst_eyes)
        possibility_lst = possibilities_white_white.copy()
        possibilities_white_color = self._find_possible_white_color_sum(lst_eyes)
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
        """finds the turn(s) with the highest strength due to the evaluation of _get_sum_situation"""
        max_turns_strength = float("-inf")
        best_turn = None
        for possibility in possibilities:
            turns_strength = self._get_sum_situation_(self._get_situation(is_active_player, possibility))
            if turns_strength > max_turns_strength:
                best_turn = possibility
                max_turns_strength = turns_strength
        return best_turn

    def cross_active(self, lst_eyes) -> List[CrossPossibility]:
        """crosses the best known active turn"""
        super().cross_active(lst_eyes)
        sleep(1)
        possibilities = self._get_possibilities_active(lst_eyes)
        return self._find_best_turns(possibilities, True)

    def _get_possibilities_passive(self, lst_eyes) -> List[List[CrossPossibility]]:
        """creates a list of all possible fields to make a cross on (while passive player)"""
        possibility_lst = self._find_possible_white_white_sum(lst_eyes)
        assert (self.board.penalties < 4)
        possibility_lst.append([CrossPossibility(4, 1)])
        # possibility_lst.append([CrossPossibility(None, None)])
        possibility_lst.append([])
        return possibility_lst

    def cross_passive(self, lst_eyes):
        """crosses the best known passive turn"""
        super().cross_passive(lst_eyes)
        possibilities = self._get_possibilities_passive(lst_eyes)
        return self._find_best_turns(possibilities, False)

    def _find_possible_white_white_sum(self, lst_eyes) -> List[List[CrossPossibility]]:
        """finds all possible fields that can be crossed with the sum of the 2 white dice"""
        possibilities_white_white = []
        white_dice_sum = lst_eyes[0] + lst_eyes[1]
        for row in Row:
            possibilities_white_white.extend(self.check_possibility_rules(row, white_dice_sum))
        return possibilities_white_white

    def _find_possible_white_color_sum(self, lst_eyes):
        """finds all possible fields that can be crossed with the sum of 1 white and 1 colored dice"""
        possibilities_white_color = []
        for color in Row:
            for white in range(2):
                white_color_sum = lst_eyes[white] + lst_eyes[color + 2]
                possibilities_white_color.extend(self.check_possibility_rules(color, white_color_sum))
        return possibilities_white_color

    def check_possibility_rules(self, row, white_plus_a_dice_sum) -> List[List[CrossPossibility]]:
        """checks witch possible fields are allowed to be crossed"""
        possibilities_white_plus_a_dice = []
        if row in (Row.RED, Row.YELLOW):
            if not self.completed_lines[row] and self.board.row_limits[row] < white_plus_a_dice_sum and (
                    (self.board.row_numbers[row] >= 5 and white_plus_a_dice_sum == 12) or white_plus_a_dice_sum < 12):
                possibilities_white_plus_a_dice.append([CrossPossibility(row, white_plus_a_dice_sum)])
        else:
            if not self.completed_lines[row] and self.board.row_limits[row] > white_plus_a_dice_sum and (
                    (self.board.row_numbers[row] >= 5 and white_plus_a_dice_sum == 2) or white_plus_a_dice_sum > 2):
                possibilities_white_plus_a_dice.append([CrossPossibility(row, white_plus_a_dice_sum)])
        return possibilities_white_plus_a_dice

