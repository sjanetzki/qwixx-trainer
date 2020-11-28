"""This file gives the opportunity to play Qwixx as a human player; not a UI;
 place where valid turns are 'translated' into a standardized format"""
from player import Player


class HumanPlayer(Player):
    """creates an environment for a human Player to play the game in conformity with the rules"""

    def cross_passive(self, lst_eyes, valid_turns, completed_lines):
        """chooses one valid cross or skips"""
        super().cross_passive(lst_eyes, valid_turns, completed_lines)

        assert (self.ui is not None)
        wish = self.ui.get_turn()
        if wish != "skip":
            return [wish]
        return []

    def cross_active(self, lst_eyes, valid_turns, completed_lines, turn_index):
        """chooses two valid crosses in succession; 2nd cross can be 'skip'"""
        super().cross_active(lst_eyes, valid_turns, completed_lines)
        assert (self.ui is not None)

        # get 1st turn
        while turn_index == 0:
            wish = self.ui.get_turn()
            # active player is not allowed to skip first cross
            if wish == "skip":
                self.inform_about_invalid_turn()
            else:
                return [wish]

        # get 2nd turn
        wish = self.ui.get_turn()
        if wish != "skip":
            return [wish]
        return []
