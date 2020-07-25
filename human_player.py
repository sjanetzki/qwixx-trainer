from player import Player


class HumanPlayer(Player):

    def cross_passive(self, lst_eyes):
        super().cross_passive(lst_eyes)

        assert (self.ui is not None)
        wish = self.ui.get_turn()
        if wish != "skip":
            return [wish]
        return []

    def cross_active(self, lst_eyes, turn_index):
        super().cross_active(lst_eyes)

        white_0 = lst_eyes[0]
        white_1 = lst_eyes[1]
        red = lst_eyes[2]
        yellow = lst_eyes[3]
        green = lst_eyes[4]
        blue = lst_eyes[5]

        print(" You got white_0 {}".format(white_0) + " and white_1 {}".format(white_1))
        print("Your Colors are red {}".format(red) + ", yellow {}".format(yellow) + ", green {}".format(green) +
              ", blue {}.".format(blue))
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

    def end(self, points):
        print("Your points: {}".format(points))
