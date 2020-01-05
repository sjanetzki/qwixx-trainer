from w2_dice_player_ga import Player


class SimpleBot(Player):
    def cross_active(self, lst_eyes):
        self.wish = (4, 1)
        return [self.wish]

    def cross_passive(self, lst_eyes):
        return [None]
