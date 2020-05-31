from player import Player


class HumanPlayer(Player):

    def cross_passive(self, lst_eyes):
        super().cross_passive(lst_eyes)

        assert (self.ui is not None)
        return [self.ui.get_turn()]

    def cross_active(self, lst_eyes):
        super().cross_active(lst_eyes)

        wish = list()
        white_0 = lst_eyes[0]
        white_1 = lst_eyes[1]
        red = lst_eyes[2]
        yellow = lst_eyes[3]
        green = lst_eyes[4]
        blue = lst_eyes[5]

        print(" You got white_0 {}".format(white_0) + " and white_1 {}".format(white_1))
        print("Your Colors are red {}".format(red) + ", yellow {}".format(yellow) + ", green {}".format(green) +
              ", blue {}.".format(blue))
        assert(self.ui is not None)
        wish.append(self.ui.get_turn())
        wish.append(self.ui.get_turn())
        return wish

    def end(self, points):
        print("Your points: {}".format(points))
