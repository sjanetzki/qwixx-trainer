"""This file creates the players of Qwixx, devides them into subclasses (human, SimpleBot, and AI) and is the place
where decisions are made."""

from board import Board
import numpy as np
from abc import ABC, abstractmethod
from copy import deepcopy


class CrossPossibility:
    """puts row and eyes of a button into a precise string format"""
    def __init__(self, row, eyes):
        self.row = row
        self.eyes = eyes

    def __repr__(self):
        return "cp(" + str(self.row) + ", " + str(self.eyes) + ")"


class Player(ABC):
    """makes all decision for doing crosses and informs the player about the state of the boards"""
    def __init__(self, name, opponents, ui=None):
        self.name = name
        self.opponents = opponents
        self.ui = ui
        self.board = Board()         # own board
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(Board())     # list with board of the others # todo avoid duplicated boards
        self.wish = (-1, -1)
        self.completed_lines = [False, False, False, False]
        self.lst_eyes = [0, 0, 0, 0, 0, 0]

    def start_new_game(self):
        """sets up a new game"""
        self.board = Board()
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(Board())

    def cross_active(self, lst_eyes):
        """gives UI information about (active) crosses to make"""
        if self.ui is None:
            return
        self.ui.lst_eyes = lst_eyes
        self.ui.is_active_player = True

    def cross_passive(self, lst_eyes):
        """gives UI information about (passive) crosses to make"""
        if self.ui is None:
            return
        self.ui.lst_eyes = lst_eyes
        self.ui.is_active_player = False

    def inform(self, boards, completed_lst, own_index):
        """informs about boards of all players and updates the knowledge about completed lines/rows"""
        self.board = boards[own_index]
        self._update_ui()
        for player_index in range(len(boards)):
            if player_index == own_index:
                continue
            if own_index > player_index:
                self.others[player_index] = boards[player_index]
            else:
                self.others[player_index - 1] = boards[player_index]
        self.completed_lines = completed_lst

    def inform_about_invalid_turn(self):
        """informs UI about an invalid turn done by the (human) player"""
        assert(self.ui is not None)
        self.ui.is_turn_invalid = True

    def _update_ui(self):
        """updates crosses on the UI"""
        if self.ui is None:
            return
        self.ui.penalties = self.board.penalties
        self.ui.crosses_by_color = self.board.crosses_by_color
        self.ui.show_board()

    def _get_situation(self, is_active_player=None, turns=None):
        """creates an numpy array (situation) that describes all boards"""
        if turns is None:
            turns = [None]
        player_count = self.opponents + 1
        situation = np.zeros((player_count * 9,))
        for player_index in range(player_count):
            # highest player_index is the own index
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
        """calculates current points of all player"""
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
        """returns points of own situation"""
        return self._get_points_situation_(self._get_situation())[-1]  # todo calculate points only for this player

    def display(self):
        """prints the own board"""
        print("number of opponents: {}".format(self.opponents))
        print("{}´s BOARD: ".format(self.name))
        self.board.show()

    def end(self, points):
        """prints the own points"""
        print(self.name + "´s" + " points: {}".format(points))
