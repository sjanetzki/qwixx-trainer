from w2_dice_dice import Dice as dice
from w2_dice_board import Board as board
# from w2_dice_player import Human as human
from w2_dice_aiplayer import AI as ai
import numpy as np


class Game:
    def __init__(self, lst_player):
        self.player_count = len(lst_player)
        self.lst_player = lst_player
        self.lst_boards = []
        self.lst_locks = []
        for index in range(self.player_count):
            self.lst_boards.append(board())
        self.completed_lines = [False, False, False, False]
        self.dice = dice()
        for player in lst_player:
            player.start_new_game()

    def is_completed(self) -> bool:
        for player_index in range(self.player_count):
            penalties = self.lst_boards[player_index].penalties
            assert(penalties in range(5))
            if penalties == 4:
                return True
            for color in range(4):
                if self.lst_boards[player_index].row_limits[color] in (1, 13):
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

    def play(self) -> None:
        round = 1
        while True:
            # print("round: {}".format(round))
            for active_player_index in range(self.player_count):
                lst_eyes = self.dice.throw()
                turns_per_player = []
                for active_or_passive_player_index in range(self.player_count):
                    player = self.lst_player[active_or_passive_player_index]
                    if active_player_index != active_or_passive_player_index:
                        wish = player.cross_passive(lst_eyes)
                    else:
                        wish = player.cross_active(lst_eyes)
                    turns_per_player.append(wish)

                for player_index in range(self.player_count):
                    turns = turns_per_player[player_index]
                    for turn in turns:
                        # if turn is not None:
                        assert(self.lst_boards[player_index].cross(turn, self.completed_lines,
                                                                   player_index == active_player_index))  # hier x gesetzt
                        # else:
                        #     if turns[0] is None:
                        #         self.lst_player[0].cross_passive(lst_eyes)
                        #     elif turns[1] is None:
                        #         self.lst_player[1].cross_passive(lst_eyes)
                        #     else:
                        #         self.lst_player[2].cross_active(lst_eyes)           # hier müsste eine Schleife hin
                for player_index in range(self.player_count):
                    self.lst_player[player_index].inform(self.lst_boards, self.completed_lines, player_index)
                if self.is_completed():
                    return
            round += 1

# game = Game([human("meep", 2), ai("gans", 2, np.random.randn(27), 0), player("glueck", 2)], 3)
# game = Game([ai("alice", 2, np.random.randn(27), 0), ai("bob", 2, np.random.randn(27), 0),
#              ai("cia", 2, np.random.randn(27), 0)], 3)
game = Game([ai("alice", 2, np.random.randn(27)), ai("bob", 2, np.random.randn(27)),
             ai("cia", 2, np.random.randn(27))])

def test():
    print(game.completed())
    print("expected result for test 1:")
    print("False")
    print("-----------------------------------------------------------------------------------------------------------")

    print(game.play())
    print("expected result for test 2:")
    print("None")
    print("-----------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
    # test()
    game.play()

# points: [^-]\d