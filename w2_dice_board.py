"""This file creates the board of Qwixx, sets valid crosses and calculates the total points."""
import numpy as np
import pygame
from enum import IntEnum


class Row(IntEnum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3

class Board:
    """does everything that happens on the board"""
    def __init__(self):
        self.row_limits = np.array([-1, -1, 14, 14])     # last crossed value in the row # todo schönere lsg für Werte
        self.row_numbers = np.array([0, 0, 0, 0])        # number of crosses in a row
        self.penalties = 0

    def show(self) -> None:
        """prints the board as a string"""
        row = [0, 1, 2, 3]

        row[0] = [" 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "11", "12", " 0"]
        row[1] = [" 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", "11", "12", " 0"]
        row[2] = ["12", "11", "10", " 9", " 8", " 7", " 6", " 5", " 4", " 3", " 2", " 0"]
        row[3] = ["12", "11", "10", " 9", " 8", " 7", " 6", " 5", " 4", " 3", " 2", " 0"]

        join_r = ' '.join(row[0])
        join_y = ' '.join(row[1])
        join_g = ' '.join(row[2])
        join_b = ' '.join(row[3])
        print("red:    {}".format(join_r))
        print("yellow: {}".format(join_y))
        print("green:  {}".format(join_g))
        print("blue:   {}".format(join_b))
        if self.penalties == 0:
            print("penalties: 0")
        else:
            print("penalties: {}".format(self.penalties))

    def show_better(self) -> None:
        """shows board as a with pygame functions"""
        pass
        # Initialize the game engine
        pygame.init()

        black = (0, 0, 0)                      # upper- or lowercase letters?
        dark_grey = (81, 81, 81)
        light_grey = (229, 229, 229)
        white = (255, 255, 255)
        red = (255, 103, 115)
        yellow = (251, 212, 85)
        green = (142, 220, 166)
        blue = (149, 198, 248)
        green_vibrant = (126, 199, 0)
        red_vibrant = (255, 0, 50)

        size = (1737, 2774)
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption("Qwixx Board")

        # Loop until the user clicks the close button.
        done = False
        clock = pygame.time.Clock()

        # Loop as long as done == False
        while not done:

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

            # Clear the screen and set the screen background
            screen.fill(light_grey)

            # Draw a rectangle
            pygame.draw.rect(screen, black, [20, 20, 250, 100], 2)

            # Select the font to use, size, bold, italics
            font = pygame.font.SysFont('Calibri', 25, True, False)

            # Render the text. "True" means anti-aliased text.
            # Black is the color. This creates an image of the
            # letters, but does not put it on the screen
            text = font.render("My text", True, dark_grey)

            # Put the image of the text on the screen at 250x250
            screen.blit(text, [250, 250])

            # Go ahead and update the screen with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pygame.display.flip()

            # This limits the while loop to a max of 60 times per second.
            # Leave this out and we will use all CPU we can.
            clock.tick(60)

        # Be IDLE friendly
        pygame.quit()

    def cross(self, position, completed_lines, is_active_player) -> bool:
        """sets the crosses chosen by the player after checking their validity, returns True if the turn is valid"""
        row = position.row
        eyes = position.eyes
        if row is None:
            if is_active_player:
                print("A")
                return False
            else:
                return True
        if row not in range(5):
            print("B")
            return False
        if row == 4:
            if self.penalties < 5:
                self.penalties += 1
                return True
            else:
                print("C")
                return False

        # make a cross in a colored row
        if eyes not in range(2, 13):
            print("G")
            return False
        if completed_lines[row]:                  # Reihe zu -> nichts eintragen
            print("D")
            print(completed_lines)
            print(row)
            print(self.row_limits)
            return False

        if row in (Row.RED, Row.YELLOW):
            cross_last_number = eyes == 12
        else:
            cross_last_number = eyes == 2

        if self.row_numbers[row] < 5 and cross_last_number:
            print("E")
            return False

        if row in (Row.RED, Row.YELLOW) and self.row_limits[row] < eyes:
            self.row_limits[row] = eyes
            self.row_numbers[row] += 1
            if cross_last_number:
                self.row_limits[row] += 1
                self.row_numbers[row] += 1
            return True
        elif row in (Row.GREEN, Row.BLUE) and self.row_limits[row] > eyes:
            self.row_limits[row] = eyes
            self.row_numbers[row] += 1
            if cross_last_number:
                self.row_limits[row] -= 1
                self.row_numbers[row] += 1
            return True
        else:
            print("F")
            return False


def test():
    """tests whether the board is working right or not"""

    board = Board()
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  9 10 11 12  0")
    print("yellow:  2  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 0")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((0, 6), [False, False, True, False]))
    print("expected: True")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  x  7  8  9 10 11 12  0")
    print("yellow:  2  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 0")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((3, 14), [False, False, False, True]))
    print("")
    print("expected result:")
    print("False")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((-3, 12), [False, False, True, False]))
    print("")
    print("expected result: ")
    print("False")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((1, 6), [False, True, True, False]))
    print("")
    print("expected result : ")
    print("False")                   # Bedingungen nicht erfüllt
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.calculate_points())
    print("")
    print("expected result: ")
    print("1")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((0, 7), [False, False, True, False]))
    print("expected: True")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  x  8  9 10 11 12  0")
    print("yellow:  2  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 0")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((0, 9), [False, False, True, False]))
    print("expected: True")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  x 10 11 12  0")
    print("yellow:  2  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 0")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((1, 2), [False, False, True, False]))
    print("expected: True")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  x 10 11 12  0")
    print("yellow:  x  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 0")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((4, 0), [False, False, True, False]))

    print(board.calculate_points())
    print("")
    print("expected result: ")
    print("2")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((1, 2), [False, False, True, False]))      # set cross on cross
    print("expected: False")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  x 10 11 12  0")
    print("yellow:  x  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 1")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((0, 2), [False, False, True, False]))      # set cross on the left of another cross
    print("expected: False")
    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  x 10 11 12  0")
    print("yellow:  x  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 1")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((4, 1), [False, False, True, False]))

    print(board.calculate_points())
    print("")
    print("expected result: ")
    print("-3")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.cross((0, 10), [False, False, True, False]))
    print("expected: True")

    print(board.cross((0, 11), [False, False, True, False]))
    print("expected: True")

    print(board.cross((0, 12), [False, False, True, False]))
    print("expected: True")

    board.show()
    print("")
    print("expected result: ")
    print("red   :  2  3  4  5  6  7  8  9 10 11 12  x")
    print("yellow:  x  3  4  5  6  7  8  9 10 11 12  0")
    print("green : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("blue  : 12 11 10  9  8  7  6  5  4  3  2  0")
    print("penalties: 2")
    print("-----------------------------------------------------------------------------------------------------------")

    print(board.calculate_points())
    print("")
    print("expected result: ")
    print("19")
    print("-----------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
    test()

