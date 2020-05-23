from player import Player


class SimpleBotPlayer(Player):
    def cross_active(self, lst_eyes):
        self.wish = (4, 1)
        return [self.wish]

    def cross_passive(self, lst_eyes):
        return [None]
