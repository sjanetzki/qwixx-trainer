from player import Player


class HumanPlayer(Player):
    def help(self):
        print("Do you need help (yes/no)?")
        ans_1 = input()
        if ans_1 == "yes":
            print("Do you have questions concerning a)the goal, b) the rules for crossing, c) the rules about the dice,"
                  "d) expressions of this computer program (please select just one of the letters a to d")

    def cross_passive(self, lst_eyes):
        white_0 = lst_eyes[0]
        white_1 = lst_eyes[1]
        print("Do you want to cross number {} somewhere? (x or no)".format(white_0 + white_1))
        ans = input()
        if ans == "x" or ans == "X":
            wish = None
            while wish is None:
                print("In which row? (red, yellow, green or blue)")
                row_wish = input()
                if row_wish == "red":
                    wish = [(0, white_0 + white_1)]
                elif row_wish == "yellow":
                    wish = [(1, white_0 + white_1)]
                elif row_wish == "green":
                    wish = [(2, white_0 + white_1)]
                elif row_wish == "blue":
                    wish = [(3, white_0 + white_1)]
                else:
                    print("Please type correctly")
        else:
            "You haven't set a passive cross"
            wish = [None]
        return wish

    def cross_active(self, lst_eyes):
        wish = []
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
