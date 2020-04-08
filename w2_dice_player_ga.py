"""This file creates the players of Qwixx, devides them into subclasses (human and AI) and is the place where
 decisions are made."""

from w2_dice_board import Board as brd
import numpy as np
from abc import ABC, abstractmethod
from copy import deepcopy


class CrossPossibility:
    def __init__(self, row, eyes):
        self.row = row
        self.eyes = eyes

    def __repr__(self):
        return "cp(" + str(self.row) + ", " + str(self.eyes) + ")"


class Player(ABC):
    """makes all decision for doing crosses and informs the player about the state of the boards"""
    def __init__(self, name, opponents):
        self.name = name
        self.opponents = opponents
        self.board = brd()         # eigenes board
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(brd())     # lst mit boards der anderen # todo avoid duplicated boards
        self.wish = (-1, -1)
        self.completed_lines = [False, False, False, False]

    def start_new_game(self):
        self.board = brd()
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(brd())

    @abstractmethod
    def cross_active(self, lst_eyes):
        pass

    @abstractmethod
    def cross_passive(self, lst_eyes):
        pass

    def inform(self, boards, completed_lst, own_index):
        for player_index in range(len(boards)):
            if player_index == own_index:
                self.board = boards[player_index]
            else:
                if own_index > player_index:
                    self.others[player_index] = boards[player_index]
                else:
                    self.others[player_index - 1] = boards[player_index]
        self.completed_lines = completed_lst

    def starting(self):
        brd.row_limit = np.array([-1, -1, -1, -1])
        brd.row_number = np.array([0, 0, 0, 0])
        brd.penalties = 0

    def _get_situation_(self, is_active_player=None, turns=None):
        if turns is None:
            turns = [None]
        player_count = self.opponents + 1
        situation = np.zeros((player_count * 9,))
        for player_index in range(player_count):
            if player_index < self.opponents:
                board = self.others[player_index]
            else:
                board = deepcopy(self.board)
                for turn in turns:
                    if turn is not None:
                        assert(is_active_player is not None)
                        assert(board.cross(turn, self.completed_lines, is_active_player))
            for parameter_type in range(9):
                if parameter_type % 2 == 0 and parameter_type != 8:
                    situation_value = board.row_numbers[parameter_type // 2]
                elif parameter_type != 8:
                    situation_value = board.row_limits[parameter_type // 2]
                else:
                    situation_value = board.penalties
                situation[player_count * parameter_type + player_index] = situation_value
        return situation

    @staticmethod
    def _get_points_situation_(situation):
        player_count = int(len(situation) / 9)
        player_situation_sums = []
        points_situation = np.zeros((player_count * 5,))  # we ignore row limits
        for situation_index in range(player_count * 4):
            colored_row_number = situation[situation_index]
            points_situation[situation_index] = (colored_row_number ** 2 + colored_row_number) / 2
        for situation_index in range(player_count * 4, player_count * 5):
            penalty = situation[situation_index]
            points_situation[situation_index] = penalty * (-5)
        for player_index in range(player_count):
            sum_points = 0
            for parameter_type in range(5):
                sum_points += points_situation[player_count * parameter_type + player_index]
            player_situation_sums.append(sum_points)
        return player_situation_sums

    def get_points(self):
        return self._get_points_situation_(self._get_situation_())[-1]  # todo calculate points only for this player

    def display(self):
        print("number of opponents: {}".format(self.opponents))
        # for i in range(self.opponents):
        #     print("board of player_{}".format(i))
        #     print(self.others[i].show())

        print("{}´s BOARD: ".format(self.name))
        self.board.show()

    def end(self, points):
        print(self.name + "´s" + " points: {}".format(points))