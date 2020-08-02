"""This file creates an algorithm (Game) that leads the game through its course"""
from dice import Dice
from board import Board
from ai_player import AiPlayer
from human_player import HumanPlayer
from ui_pygame import PyGameUi
from simple_bot_player import SimpleBotPlayer
import numpy as np


class Game:
    """role of the Game Master;
    directs the game, interacts with the players, and minds the conformity of the rules of the players' actions"""

    def __init__(self, lst_player):
        self.player_count = len(lst_player)
        self.lst_player = lst_player
        self.lst_boards = []
        for index in range(self.player_count):
            self.lst_boards.append(Board())
        self.completed_lines = [False, False, False, False]
        self.dice = Dice()
        for player in lst_player:
            player.start_new_game()

    def _is_completed(self) -> bool:
        """checks whether the game is completed"""
        for player_index in range(self.player_count):
            penalties = self.lst_boards[player_index].penalties
            assert (penalties in range(5))
            if penalties == 4:
                return True
            for color in range(4):
                if (color in (0, 1) and self.lst_boards[player_index].row_limits[color] == 13) or \
                        (color in (2, 3) and self.lst_boards[player_index].row_limits[color] == 1):
                    self.completed_lines[color] = True
        if sum(self.completed_lines) >= 2:
            return True
        return False

    def compute_ranking(self):
        """computes a ranking of the players by points after the game is completed; function used by trainer"""
        ranking = []
        if not self._is_completed():
            return None
        for player in self.lst_player:
            points = player.get_points()
            ranking.append((player, points))
        ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
        return ranking

    def _make_valid_turn(self, player_index, turn, is_active_player, lst_eyes, previous_turn=None):
        """checks validity of a turn"""
        is_turn_valid = turn.row == 4 \
                        or (is_active_player
                            and (lst_eyes[0] + lst_eyes[1] == turn.eyes
                                 or lst_eyes[0] + lst_eyes[turn.row + 2] == turn.eyes
                                 or lst_eyes[1] + lst_eyes[turn.row + 2] == turn.eyes)) \
                        or (not is_active_player
                            and lst_eyes[0] + lst_eyes[1] == turn.eyes)

        if is_turn_valid:
            is_turn_valid = self.lst_boards[player_index].cross(turn, self.completed_lines, is_active_player)
        if not (is_turn_valid or isinstance(self.lst_player[player_index], HumanPlayer)):
            assert (is_turn_valid or isinstance(self.lst_player[player_index], HumanPlayer))
        if not is_turn_valid:
            self.lst_player[player_index].inform_about_invalid_turn()
        return is_turn_valid

    def _make_turns_for_active_human_player(self, lst_eyes, player_index, player, is_active_player):
        """lets a human player cross active until the turn chosen is valid"""
        is_turn_valid = False
        turn_index = 0
        while not is_turn_valid:
            turns = player.cross_active(lst_eyes, turn_index)
            assert (len(turns) == 1)
            is_turn_valid = self._make_valid_turn(player_index, turns[0], is_active_player, lst_eyes)
            previous_turn = turns[0]
        self.lst_player[player_index].inform(self.lst_boards, self.completed_lines, player_index)

        turn_index += 1
        is_turn_valid = False
        while not is_turn_valid:
            turns = player.cross_active(lst_eyes, turn_index)
            assert (len(turns) <= 1)
            if len(turns) != 0:
                is_turn_valid = self._make_valid_turn(player_index, turns[0], is_active_player, lst_eyes, previous_turn)
            else:
                is_turn_valid = True

    def _make_turns_for_ai_or_passive_human_player(self, lst_eyes, player_index, player, is_active_player):
        """lets an AI player (passive or active) or passive human player cross until the turn chosen is valid """
        is_turn_valid = False
        while not is_turn_valid:
            if is_active_player:
                turns = player.cross_active(lst_eyes)
                assert (1 <= len(turns) <= 2)
            else:
                turns = player.cross_passive(lst_eyes)
                assert (len(turns) <= 1)
            for turn in turns:
                is_turn_valid = self._make_valid_turn(player_index, turn, is_active_player, lst_eyes)
            if len(turns) == 0:
                is_turn_valid = True

    def _direct_turns_of_all_players(self):
        """directs when the players are prompted to do their turns"""
        for active_player_index in range(self.player_count):
            lst_eyes = self.dice.throw()
            for player_index in range(self.player_count):
                player = self.lst_player[player_index]
                is_active_player = player_index == active_player_index
                if isinstance(player, HumanPlayer) and is_active_player:
                    self._make_turns_for_active_human_player(lst_eyes, player_index, player, is_active_player)
                else:
                    self._make_turns_for_ai_or_passive_human_player(lst_eyes, player_index, player, is_active_player)

            # inform all players about new game situation AFTER they made their turns
            for player_index in range(self.player_count):
                self.lst_player[player_index].inform(self.lst_boards, self.completed_lines, player_index)
            if self._is_completed():
                exit(0)     # print results

    def play(self) -> None:
        """manages the run of a game (Game Master) until the game is completed; also used by the trainer"""
        while True:
            self._direct_turns_of_all_players()


if __name__ == "__main__":
    ui = PyGameUi()
    ui.show_board()
    # game = Game([AiPlayer("meep", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18), ui),
    # AiPlayer("gans", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18))])
    game = Game([HumanPlayer("meep", 2, ui),
                 AiPlayer("meeep", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18))])
    game.play()
