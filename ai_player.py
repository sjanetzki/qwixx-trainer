"""This file creates the 'brain' of an AI-player -> place of decision process what to do in the next turn"""
from time import sleep

import numpy as np

from player import CrossPossibility, Player
from typing import List
from copy import copy
import math


class SampleStrategies:
    bodo_quadratic_factor = np.array([0.0, 0, 0, 0])
    bodo_linear_factor = np.array([1.0, -0.5, 0.5, -2.5])
    bodo_bias = np.array([0.0, 0, -6, 0])

    caira_quadratic_factor = np.array([0.5, 0, 0, 0])
    caira_linear_factor = np.array([0.5, 0, 0, -5])
    caira_bias = np.array([0.0, 0.0, 0.0, 0.0])         # 0.0 for float type (important for mutation)


class AiPlayer(Player):
    """an AI Player that decides on its own which crosses to make by evaluation;
    individual is characterized by its strategy"""

    strategy_length = 4  # number x; limit r/y; limit g/b; penalty

    def __init__(self, name, quadratic_factor, linear_factor, bias, ui=None):
        super().__init__(name, ui)
        self.quadratic_factor = copy(quadratic_factor)
        self.linear_factor = copy(linear_factor)
        self.bias = copy(bias)

    def __repr__(self):
        return "AI(" + self.name + ")"

    def _get_sum_situation_(self, hypothetical_situation) -> float:
        """evaluates the quality of a hypothetical situation that will be the situation after this turn"""
        situation_quality = 0
        assert (len(self.quadratic_factor) == len(self.linear_factor) == len(self.bias) == AiPlayer.strategy_length
                and len(hypothetical_situation) == Player.situation_length)
        quadratic_factor_extended = self._extend_strategy_length(self.quadratic_factor)
        linear_factor_extended = self._extend_strategy_length(self.linear_factor)
        bias_extended = self._extend_strategy_length(self.bias)

        for index in range(len(hypothetical_situation)):
            situation_quality += math.pow(hypothetical_situation[index], 2) * quadratic_factor_extended[index]
            situation_quality += hypothetical_situation[index] * linear_factor_extended[index]
            situation_quality += bias_extended[index]
        return situation_quality

    @staticmethod
    def _extend_strategy_length(strategy_part):
        """extends a part of the strategy to make it fit the dimensions of the situation"""
        assert (Player.situation_length == 9 and len(strategy_part) == 4)
        strategy_part_extended = np.zeros((Player.situation_length,))
        strategy_part_extended[0] = strategy_part[0]
        strategy_part_extended[1] = strategy_part[1]
        strategy_part_extended[2] = strategy_part[0]
        strategy_part_extended[3] = strategy_part[1]
        strategy_part_extended[4] = strategy_part[0]
        strategy_part_extended[5] = strategy_part[2]
        strategy_part_extended[6] = strategy_part[0]
        strategy_part_extended[7] = strategy_part[2]
        strategy_part_extended[8] = strategy_part[3]
        return strategy_part_extended

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
        # sleep(0.3)
        return self._find_best_turns(valid_turns, completed_lines, True)

    def cross_passive(self, lst_eyes, valid_turns, completed_lines):
        """crosses the best known passive turn"""
        super().cross_passive(lst_eyes, valid_turns, completed_lines)
        return self._find_best_turns(valid_turns, completed_lines, False)
