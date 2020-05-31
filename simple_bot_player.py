from player import Player
from player import CrossPossibility


class SimpleBotPlayer(Player):
    def cross_active(self, lst_eyes):
        super().cross_active(lst_eyes)
        return [CrossPossibility(4, 1)]

    def cross_passive(self, lst_eyes):
        super().cross_passive(lst_eyes)
        return [None]
