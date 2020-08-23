"""This file creates the players of Qwixx, divides them into subclasses (human, SimpleBot, and AI) and is the place
where decisions are made."""

from board import Board, Row
import numpy as np
from abc import ABC
from copy import deepcopy


class CrossPossibility(object):
    """puts row and eyes of a button into a precise string format"""
    def __init__(self, row, eyes):
        assert (isinstance(row, Row) or row == 4)
        assert (row != 4 or eyes is None)
        self.row = row
        self.eyes = eyes

    def __repr__(self):
        return "cp(" + str(self.row) + ", " + str(self.eyes) + ")"

    def __eq__(self, other):
        return other != "skip" and self.row == other.row and self.eyes == other.eyes


class Player(ABC):
    """makes all decision for doing crosses and informs the player about the state of the boards"""
    def __init__(self, name, opponents, ui=None):        # !!! remember to reset all variables update start_new_game !!!
        self.name = name
        self.opponents = opponents
        self.ui = ui
        self.board = Board()         # own board
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(Board())     # list with board of the others # todo #1 avoid duplicated boards

    def start_new_game(self) -> None:
        """sets up a new game"""
        self.board = Board()
        self.others = []
        for opponent_index in range(self.opponents):
            self.others.append(Board())

    def cross_active(self, lst_eyes, valid_turns) -> None:
        """gives UI information about (active) crosses to make"""
        if self.ui is None:
            return
        self.ui.lst_eyes = lst_eyes
        self.ui.is_active_player = True

    def cross_passive(self, lst_eyes, valid_turns) -> None:
        """gives UI information about (passive) crosses to make"""
        if self.ui is None:
            return
        self.ui.lst_eyes = lst_eyes
        self.ui.is_active_player = False

    def inform(self, boards, own_index) -> None:
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

    def inform_about_invalid_turn(self) -> None:
        """informs UI about an invalid turn done by the (human) player"""
        assert(self.ui is not None)
        self.ui.is_turn_invalid = True

    def _update_ui(self) -> None:
        """updates crosses on the UI"""
        if self.ui is None:
            return
        self.ui.penalties = self.board.penalties
        self.ui.crosses_by_color = self.board.crosses_by_color
        self.ui.show_board()

    def show_options(self, possibility_lst) -> None:
        """gives the UI the order to show possible fields to make a cross on"""
        if self.ui is None:
            return
        self.ui.show_options_on_board(possibility_lst)

    def _get_situation(self, completed_lines=None, is_active_player=None, turns=None):
        """creates an numpy array (situation) that describes all boards"""
        if turns is None:
            turns = [None]
        player_count = self.opponents + 1
        situation = np.zeros((player_count * 9,))
        for player_index in range(player_count):
            # highest player_index is the own index
            if player_index < self.opponents:
                board = self.others[player_index] # todo #1 pass list as function parameter with board of all players, player knows own index
            else:
                board = deepcopy(self.board)
                for turn in turns:                          # todo split -> with/without turns
                    if turn is not None:
                        assert(is_active_player is not None)
                        board.cross(turn, completed_lines, is_active_player)
            for parameter_type in range(9):
                if parameter_type % 2 == 0 and parameter_type != 8:
                    situation_value = board.row_numbers[parameter_type // 2]
                elif parameter_type != 8:
                    situation_value = board.row_limits[parameter_type // 2]
                else:
                    situation_value = board.penalties
                situation[player_count * parameter_type + player_index] = situation_value
        return situation

    def get_points(self):
        """calculates current points of a player"""
        situation = self._get_situation()
        player_count = int(len(situation) / 9)
        player_points = 0
        player_index = player_count - 1

        # gives points for number of crosses in a row
        for row_start in range(0, player_count * 8, player_count * 2):  # will be called 4 times
            colored_row_number = situation[row_start + player_index]
            player_points += (colored_row_number ** 2 + colored_row_number) / 2

        # calculates points for penalties
        penalty = situation[player_count * 8 + player_index]
        player_points += penalty * (-5)
        return player_points

    def end(self, points) -> None:
        """prints the own points"""
        print(self.name + "´s" + " points: {}".format(points))
