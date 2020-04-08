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
        self.row_limits = np.array([1, 1, 13, 13])     # last crossed value in the row
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


class PyGameBoard(Board):

    def __init__(self):
        pass

    def show_background(self) -> None:
        """shows board as a with pygame functions"""
        pygame.init()
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        black = (0, 0, 0)                      # upper- or lowercase letters?
        dark_grey = (120, 120, 120)
        light_grey = (215, 215, 215)
        white = (255, 255, 255)
        light_red = (255, 156, 163)
        red = (255, 103, 115)
        light_yellow = (248, 220, 127)
        yellow = (251, 212, 85)
        light_green = (184, 221, 196)
        green = (142, 220, 166)
        light_blue = (197, 220, 242)
        blue = (149, 198, 248)
        green_vibrant = (126, 199, 0)
        red_vibrant = (255, 0, 50)

        size = (1216, 650)
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption("Qwixx Board")
        done = False
        clock = pygame.time.Clock()
        while not done:

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

            screen.fill(white)
            font = pygame.font.SysFont('letters for learners', 36, True, False)
            lock = pygame.font.SysFont('letters for learners', 64, True, False)

            pygame.draw.rect(screen, light_red, [32, 32, 1152, 118], 0)
            for field in range(0, 11):
                pygame.draw.rect(screen, red, [50 + 92 * field, 50, 80, 80], 0)
                text = font.render("{}".format(int(field + 2)), True, white)
                screen.blit(text, [80 + 92 * field, 70])
            pygame. draw.circle(screen, red, [1112, 90], 36, 0)

            pygame.draw.rect(screen, light_yellow, [32, 158, 1152, 118], 0)
            for field in range(0, 11):
                pygame.draw.rect(screen, yellow, [50 + 92 * field, 50 * 2 + 76, 80, 80], 0)
                text = font.render("{}".format(int(field + 2)), True, white)
                screen.blit(text, [80 + 92 * field, 70 * 2 + 56])
            pygame. draw.circle(screen, yellow, [1112, 90 * 2 + 36], 36, 0)

            pygame.draw.rect(screen, light_green, [32, 284, 1152, 118], 0)
            for field in range(0, 11):
                pygame.draw.rect(screen, green, [50 + 92 * field, 50 * 3 + 76 * 2, 80, 80], 0)
                text = font.render("{}".format(int(12 - field)), True, white)
                screen.blit(text, [80 + 92 * field, 70 * 3 + 56 * 2])
            pygame. draw.circle(screen, green, [1112, 90 * 3 + 36 * 2], 36, 0)

            pygame.draw.rect(screen, light_blue, [32, 410, 1152, 118], 0)
            for field in range(0, 11):
                pygame.draw.rect(screen, blue, [50 + 92 * field, 50 * 4 + 76 * 3, 80, 80], 0)
                text = font.render("{}".format(int(12 - field)), True, white)
                screen.blit(text, [80 + 92 * field, 70 * 4 + 56 * 3])
            pygame. draw.circle(screen, blue, [1112, 90 * 4 + 36 * 3], 36, 0)

            for row in range(4):
                text = lock.render("*", True, white)
                screen.blit(text, [1102, 90 * (row + 1) + 36 * row - 30])

            pygame.draw.rect(screen, light_grey, [784, 536, 400, 60], 0)
            for field in range(1, 5):
                pygame.draw.rect(screen, dark_grey, [970 + 10 * field + 40 * (field - 1), 546, 40, 40], 0)
            text = font.render("penalties", True, dark_grey)
            screen.blit(text, [800, 546])
            self.button(980, 567, 40, 40, light_grey, red_vibrant, 1)
            pygame.display.flip()
            # print(mouse)
            clock.tick(60)
        pygame.quit()

    def button(self, x, y, w, h, ic, ac, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        size = (1216, 650)
        screen = pygame.display.set_mode(size)
        if int(x + w) > int(mouse[0]) > x and int(y + h) > int(mouse[1]) > y:
            pygame.draw.rect(screen, ac, (x, y, w, h))
            if click[0] == 1 and action is not None:
                action()
            else:
                pygame.draw.rect(screen, ic, (x, y, w, h))
            print(mouse)

   
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
    board = PyGameBoard
    board.show_background(board)

