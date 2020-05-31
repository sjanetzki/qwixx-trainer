from dice import Dice
from board import Board
from ai_player import AiPlayer
from human_player import HumanPlayer
from ui_pygame import PyGameUi
import numpy as np


class Game:
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

    def is_completed(self) -> bool:
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
        ranking = []
        if not self.is_completed():
            return None
        for player in self.lst_player:
            points = player.get_points()
            ranking.append((player, points))
        ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
        return ranking

    def make_turn(self, player_index, turn, is_active_player, lst_eyes):
        is_turn_valid = turn.row == 4 \
                         or (is_active_player
                             and (lst_eyes[0] + lst_eyes[1] == turn.eyes
                                  or lst_eyes[0] + lst_eyes[turn.row + 2] == turn.eyes
                                  or lst_eyes[1] + lst_eyes[turn.row + 2] == turn.eyes)) \
                         or (not is_active_player
                             and lst_eyes[0] + lst_eyes[1] == turn.eyes)

        is_turn_valid &= self.lst_boards[player_index].cross(turn, self.completed_lines, is_active_player)
        if not (is_turn_valid or isinstance(self.lst_player[player_index], HumanPlayer)):
            pass
        assert (is_turn_valid or isinstance(self.lst_player[player_index], HumanPlayer))
        if not is_turn_valid:
            self.lst_player[player_index].inform_about_invalid_turn()
        return is_turn_valid

    def play(self) -> None:
        while True:
            for active_player_index in range(self.player_count):
                lst_eyes = self.dice.throw()
                is_turn_valid = False
                for player_index in range(self.player_count):
                    player = self.lst_player[player_index]
                    while not is_turn_valid:
                        if active_player_index != player_index:
                            turns = player.cross_passive(lst_eyes)
                        else:
                            turns = player.cross_active(lst_eyes)
                        for turn in turns:
                            is_turn_valid = self.make_turn(player_index, turn, player_index == active_player_index, lst_eyes)
                for player_index in range(self.player_count):
                    self.lst_player[player_index].inform(self.lst_boards, self.completed_lines, player_index)
                if self.is_completed():
                    return


if __name__ == "__main__":
    ui = PyGameUi()
    ui.show_background()
    # game = Game([AiPlayer("meep", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18), ui),
    # AiPlayer("gans", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18))])
    game = Game([HumanPlayer("meep", 2, ui),
                 AiPlayer("meeep", 2, np.random.randn(18), np.random.randn(18), np.random.randn(18))])
    game.play()
