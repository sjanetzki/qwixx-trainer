"""This file creates the 'brain' of an AI-player -> place of decision process what to do in the next turn"""
from player import CrossPossibility, Player
from typing import List
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

    def cross_active(self, lst_eyes, valid_turns) -> List[CrossPossibility]:
        """crosses the best known active turn"""
        super().cross_active(lst_eyes, valid_turns)
        # sleep(1)
        return self._find_best_turns(valid_turns, True)

    def cross_passive(self, lst_eyes, valid_turns):
        """crosses the best known passive turn"""
        super().cross_passive(lst_eyes, valid_turns)
        return self._find_best_turns(valid_turns, False)
