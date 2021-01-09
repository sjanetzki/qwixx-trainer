"""This file creates an algorithm (Game) that leads the game through its course"""
from typing import List, Tuple

from dice import Dice
from board import Board, Row
from ai_player import AiPlayer, SampleStrategies
from human_player import HumanPlayer
from player import CrossPossibility, Player
from ui_pygame import PyGameUi
import pickle


class Game:
    """role of the Game Master;
    directs the game, interacts with the players, and minds the conformity of the rules of the players' actions"""

    def __init__(self, lst_player):
        self.player_count = len(lst_player)
        self.lst_player = lst_player
        self.lst_boards = []
        for index in range(self.player_count):
            self.lst_boards.append(Board())
        self.completed_lines = [False, False, False, False]     # anybody able to complete line --> variable in game and not board
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

    def compute_ranking(self) -> List[Tuple[Player, int]]:
        """computes a ranking of the players by points after the game is completed; function used by trainer"""
        ranking = []
        for player in self.lst_player:
            points = player.get_points()
            ranking.append((player, points))
        ranking = sorted(ranking, key=lambda x: x[1], reverse=True)
        return ranking

    def _make_valid_turn(self, player_index, turn, valid_turns, is_active_player, previous_turn=None) -> bool:
        """checks validity of a turn"""
        is_turn_valid = False
        # check whether first turn and, if applicable, both turns combined, are valid
        for complete_valid_turn in valid_turns:
            if (previous_turn is None and len(complete_valid_turn) > 0 and complete_valid_turn[0] == turn) or (
                    previous_turn is not None and complete_valid_turn == [previous_turn, turn]):
                is_turn_valid = True
                break

        assert (is_turn_valid or isinstance(self.lst_player[player_index], HumanPlayer))
        if is_turn_valid:
            self.lst_boards[player_index].cross(turn, self.completed_lines, is_active_player)
        else:
            self.lst_player[player_index].inform_about_invalid_turn()
        return is_turn_valid

    def _get_possibilities_active(self, lst_eyes, player_index) -> List[List[CrossPossibility]]:
        """creates a list of all possible fields to make a cross on (while active player)"""
        possibilities_white_white = self._find_possible_white_white_sum(lst_eyes, player_index)
        possibility_lst = possibilities_white_white.copy()
        possibilities_white_color = self._find_possible_white_color_sum(lst_eyes, player_index)
        possibility_lst.extend(possibilities_white_color)

        for white_white in possibilities_white_white:
            white_white = white_white[0]
            for white_color in possibilities_white_color:
                white_color = white_color[0]
                if (white_white.row != white_color.row) or (
                        white_white.row in (Row.RED, Row.YELLOW) and white_white.eyes < white_color.eyes) or (
                        white_white.row in (Row.GREEN, Row.BLUE) and white_white.eyes > white_color.eyes):
                    possibility_lst.append([white_white, white_color])

        assert(self.lst_boards[player_index].penalties < 4)
        possibility_lst.append([CrossPossibility(4, None)])
        return possibility_lst

    def _find_possible_white_white_sum(self, lst_eyes, player_index) -> List[List[CrossPossibility]]:
        """finds all possible fields that can be crossed with the sum of the 2 white dice"""
        possibilities_white_white = []
        white_dice_sum = lst_eyes[0] + lst_eyes[1]
        for row in Row:
            possibilities_white_white.extend(self._check_possibility_rules(row, white_dice_sum, player_index))
        return possibilities_white_white

    def _find_possible_white_color_sum(self, lst_eyes, player_index):
        """finds all possible fields that can be crossed with the sum of 1 white and 1 colored dice"""
        possibilities_white_color = []
        for color in Row:
            for white in range(2):
                white_color_sum = lst_eyes[white] + lst_eyes[color + 2]
                possibilities_white_color.extend(self._check_possibility_rules(color, white_color_sum, player_index))
        return possibilities_white_color

    def _get_possibilities_passive(self, lst_eyes, player_index) -> List[List[CrossPossibility]]:
        """creates a list of all possible fields to make a cross on (while passive player)"""
        possibility_lst = self._find_possible_white_white_sum(lst_eyes, player_index)
        assert (self.lst_boards[player_index].penalties < 4)
        possibility_lst.append([CrossPossibility(4, None)])
        possibility_lst.append([])
        return possibility_lst

    def _check_possibility_rules(self, row, white_plus_a_dice_sum, player_index) -> List[List[CrossPossibility]]:
        """checks witch possible fields are allowed to be crossed"""
        possibilities_white_plus_a_dice = []
        if row in (Row.RED, Row.YELLOW):
            if not self.completed_lines[row] and self.lst_boards[player_index].row_limits[
                row] < white_plus_a_dice_sum and (
                    (self.lst_boards[player_index].row_numbers[
                         row] >= 5 and white_plus_a_dice_sum == 12) or white_plus_a_dice_sum < 12):
                possibilities_white_plus_a_dice.append([CrossPossibility(row, white_plus_a_dice_sum)])
        else:
            if not self.completed_lines[row] and self.lst_boards[player_index].row_limits[
                row] > white_plus_a_dice_sum and (
                    (self.lst_boards[player_index].row_numbers[
                         row] >= 5 and white_plus_a_dice_sum == 2) or white_plus_a_dice_sum > 2):
                possibilities_white_plus_a_dice.append([CrossPossibility(row, white_plus_a_dice_sum)])
        return possibilities_white_plus_a_dice

    def _make_turns_for_active_human_player(self, lst_eyes, player_index, player, is_active_player) -> None:
        """lets a human player cross active until the turn chosen is valid"""
        is_turn_valid = False
        turn_index = 0
        valid_turns = self._get_possibilities_active(lst_eyes, player_index)
        previous_turn = None
        self.lst_player[player_index].show_options(self._get_possibilities_active(lst_eyes, player_index))
        while not is_turn_valid:
            turns = player.cross_active(lst_eyes, valid_turns, self.completed_lines, turn_index)
            assert (len(turns) == 1)
            is_turn_valid = self._make_valid_turn(player_index, turns[0], valid_turns, is_active_player)
            previous_turn = turns[0]
        self.lst_player[player_index].inform(self.lst_boards, player_index)

        turn_index += 1
        is_turn_valid = False
        self.lst_player[player_index].show_options(self._get_possibilities_passive(lst_eyes, player_index))
        # only allow 2nd if previous turn was done with WHITE dice
        while not is_turn_valid and previous_turn.row != 4 and previous_turn.eyes == lst_eyes[0] + lst_eyes[1]:
            turns = player.cross_active(lst_eyes, valid_turns, self.completed_lines, turn_index)
            assert (len(turns) <= 1)
            if len(turns) != 0:
                is_turn_valid = self._make_valid_turn(player_index, turns[0], valid_turns, is_active_player,
                                                      previous_turn)
            else:
                is_turn_valid = True

    def _make_turns_for_ai_or_passive_human_player(self, lst_eyes, player_index, player, is_active_player) -> None:
        """lets an AI player (passive or active) or passive human player cross until the turn chosen is valid """
        is_turn_valid = False
        while not is_turn_valid:
            if is_active_player:
                valid_turns = self._get_possibilities_active(lst_eyes, player_index)
                turns = player.cross_active(lst_eyes, valid_turns, self.completed_lines)
                assert (1 <= len(turns) <= 2)
            else:
                valid_turns = self._get_possibilities_passive(lst_eyes, player_index)
                turns = player.cross_passive(lst_eyes, valid_turns, self.completed_lines)
                assert (len(turns) <= 1)

            if len(turns) == 0:
                is_turn_valid = True
            else:
                is_turn_valid = self._make_valid_turn(player_index, turns[0], valid_turns, is_active_player)
            if len(turns) == 2:
                is_turn_valid = self._make_valid_turn(player_index, turns[1], valid_turns, is_active_player, turns[0])

    def play(self, prints_points=False) -> None:
        """manages the run of a game (Game Master) until the game is completed; directs when the players are prompted to
         do their turns; also used by the trainer"""
        game_in_progress = True
        while game_in_progress:
            for active_player_index in range(self.player_count):
                lst_eyes = self.dice.throw_dice()
                for player_index in range(self.player_count):
                    player = self.lst_player[player_index]
                    is_active_player = player_index == active_player_index
                    if isinstance(player, HumanPlayer) and is_active_player:
                        self._make_turns_for_active_human_player(lst_eyes, player_index, player, is_active_player)
                    else:
                        self._make_turns_for_ai_or_passive_human_player(lst_eyes, player_index, player,
                                                                        is_active_player)
                if prints_points:
                    print(self.compute_ranking())

                if self._is_completed():
                    game_in_progress = False

                # inform all players about new game situation AFTER they made their turns
                for player_index in range(self.player_count):
                    self.lst_player[player_index].inform(self.lst_boards, player_index)

                if not game_in_progress:
                    break                   # todo execute turns for all players and evaluate turns (separate)


def load_best_ai():
    """loads the AI that was saved"""
    file = open("best_ai.dat", "rb")
    best_ai = pickle.load(file)
    file.close()
    return best_ai


if __name__ == "__main__":
    ui = PyGameUi()
    ui.show_board()
    # ai_opponent = load_best_ai()



    # game = Game([HumanPlayer("meep", ui),
                 # AiPlayer("meeep", np.random.randn(18), np.random.randn(18), np.random.randn(18))])

    game = Game([HumanPlayer("visitor", ui),
                 AiPlayer("", SampleStrategies.alpha_qwixx_quadratic_factor, SampleStrategies.alpha_qwixx_linear_factor,
                          SampleStrategies.alpha_qwixx_bias)])
    game.play(True)
