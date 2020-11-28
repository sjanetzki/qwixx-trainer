from player import Player
from player import CrossPossibility


class SimpleBotPlayer(Player):
    """a Player that has no intelligence; only crosses penalties"""

    def cross_active(self, lst_eyes, valid_turns, completed_lines):
        """crosses penalty if active"""
        super().cross_active(lst_eyes, valid_turns, completed_lines)
        assert (self.board.penalties < 4)
        return [CrossPossibility(4, None)]

    def cross_passive(self, lst_eyes, valid_turns, completed_lines):
        """crosses nothing (skips) if passive"""
        super().cross_passive(lst_eyes, valid_turns, completed_lines)
        return []
