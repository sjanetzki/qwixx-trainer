from w2_dice_player_ga import Player


class Human(Player):
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
        print("Do you want to cross number {} somewhere? (x or no)".format(white_0 + white_1))
        ans = input()
        if ans == "x" or ans == "X":
            while len(wish) == 0:
                print("In which row? (red, yellow, green or blue)")
                row_wish = input()
                if row_wish == "red":
                    wish.append((0, white_0 + white_1))
                elif row_wish == "yellow":
                    wish.append((1, white_0 + white_1))
                elif row_wish == "green":
                    wish.append((2, white_0 + white_1))
                elif row_wish == "blue":
                    wish.append((3, white_0 + white_1))
                else:
                    print("Please type correctly")
        else:
            "You haven't set a white cross"

        print(" You got white_0 {}".format(white_0) + " and white_1 {}".format(white_1))
        print("Your Colors are red {}".format(red) + ", yellow {}".format(yellow) + ", green {}".format(green) +
              ", blue {}.".format(blue))
        print(" Do you want to make a cross in one of the rows? (x/ no)")
        ans_1 = input()
        while ans_1 != "x" and ans_1 != "no":
            print("Com'on, don't be stupid! Ok, you get another input (x or no)")
            ans_1 = input()
        if ans_1 == "no":
            wish.append((4, self.board.penalties))
            print("self.wish: {}".format(wish))
            return wish
        else:
            print("Which colored dice? (red, yellow, green or blue)")
            ans_2 = input()
            while ans_2 != "red" and ans_2 != "yellow" and ans_2 != "green" and ans_2 != "blue" and ans_2 != "help":
                print("Which colored dice? (red, yellow, green or blue)")
                ans_2 = input()
            print("which white dice? (white_0 or white_1)")
            ans_3 = input()
            while ans_3 != "white_0" and ans_3 != "white_1" and ans_3 != "help":
                print("which white dice? (white_0 or white_1)")
                ans_3 = input()

            if ans_2 == "red":
                row = 0
                a = lst_eyes[2]
            elif ans_2 == "yellow":
                row = 1
                a = lst_eyes[3]
            elif ans_2 == "green":
                row = 2
                a = lst_eyes[4]
            elif ans_2 == "blue":
                row = 3
                a = lst_eyes[5]

            if ans_3 == "white_0":
                b = lst_eyes[0]
            elif ans_3 == "white_1":
                b = lst_eyes[1]

            wish.append((row, (a + b)))
            return wish

    def inform(self, crosses_lst, completed_rows):
        for i in range(self.opponents):
            lst = crosses_lst[i]
            for c in lst:
                if c is not None:
                    print(self.others[i].cross(c, completed_rows))
        lst = crosses_lst[-1]
        for c in lst:
            if c is not None:
                print(self.board.cross(c, completed_rows))
        self.board.show()

    def end(self, points):
        print("Your points: {}".format(points))
