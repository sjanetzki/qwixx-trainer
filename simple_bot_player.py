from player import Player
from player import CrossPossibility


class SimpleBotPlayer(Player):
    """a Player that has no intelligence; only crosses penalties"""

    def cross_active(self, lst_eyes, valid_turns):
        """crosses penalty if active"""
        super().cross_active(lst_eyes, valid_turns)
        assert (self.board.penalties < 4)
        return [CrossPossibility(4, None)]

    def cross_passive(self, lst_eyes, valid_turns):
        """crosses nothing (skips) if passive"""
        super().cross_passive(lst_eyes, valid_turns)
        return []
