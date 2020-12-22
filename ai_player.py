"""This file creates the 'brain' of an AI-player -> place of decision process what to do in the next turn"""
from player import CrossPossibility, Player
from typing import List
from time import sleep
import math


class AiPlayer(Player):
    """an AI Player that decides on its own which crosses to make by evaluation;
    individual is characterized by its strategy"""

    def __init__(self, name, quadratic_factor, linear_factor, bias, ui=None):
        super().__init__(name, ui)
        self.quadratic_factor = quadratic_factor
        self.linear_factor = linear_factor
        self.bias = bias

    def __repr__(self):
        return "AI(" + self.name + ")"

    def _get_sum_situation_(self, hypothetical_situation) -> float:
        """evaluates the quality of a hypothetical situation that will be the situation after this turn"""
        situation_quality = 0
        assert(len(hypothetical_situation) == len(self.quadratic_factor) == len(self.linear_factor) == len(self.bias))
        for index in range(len(hypothetical_situation)):
            situation_quality += math.pow(hypothetical_situation[index], 2) * self.quadratic_factor[index]
            situation_quality += hypothetical_situation[index] * self.linear_factor[index]
            situation_quality += self.bias[index]
        return situation_quality

    def _find_best_turns(self, possibilities, completed_lines, is_active_player) -> List[CrossPossibility]:
        """finds the turn(s) with the highest strength due to the evaluation of _get_sum_situation"""
        max_turns_strength = float("-inf")
        best_turn = None
        for possibility in possibilities:
            situation = self._get_hypothetical_situation_after_turns(completed_lines, is_active_player, possibility)
            turns_strength = self._get_sum_situation_(situation)
            if turns_strength > max_turns_strength:
                best_turn = possibility
                max_turns_strength = turns_strength
        return best_turn

    def cross_active(self, lst_eyes, valid_turns, completed_lines) -> List[CrossPossibility]:
        """crosses the best known active turn"""
        super().cross_active(lst_eyes, valid_turns, completed_lines)
        # sleep(0.5)
        return self._find_best_turns(valid_turns, completed_lines, True)

    def cross_passive(self, lst_eyes, valid_turns, completed_lines):
        """crosses the best known passive turn"""
        super().cross_passive(lst_eyes, valid_turns, completed_lines)
        return self._find_best_turns(valid_turns, completed_lines, False)
