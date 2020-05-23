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


class PyGameBoard(object):

    black = (0, 0, 0)  # upper- or lowercase letters?
    dark_grey = (120, 120, 120)
    light_grey = (215, 215, 215)
    white = (255, 255, 255)
    light_red = (255, 156, 163)
    red = (255, 103, 115)
    light_yellow = (248, 220, 127)
    yellow = (251, 212, 85)
    yellow_vibrant = (255, 195, 0)
    light_green = (184, 221, 196)
    green = (142, 220, 166)
    light_blue = (197, 220, 242)
    blue = (149, 198, 248)
    blue_vibrant = (0, 129, 255)
    green_vibrant = (62, 224, 109)
    red_vibrant = (255, 0, 20)

    def __init__(self):
        size = (1216, 650)
        self.screen = pygame.display.set_mode(size)
        self.mouse_down = False
        self.crosses_red = set()
        self.crosses_yellow = set()
        self.crosses_green = set()
        self.crosses_blue = set()
        self.penalties = 0

    def show_background(self) -> None:
        """shows board as a with pygame functions"""
        pygame.init()
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        pygame.display.set_caption("Qwixx Board")
        done = False
        clock = pygame.time.Clock()
        while not done:

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

            self.screen.fill(PyGameBoard.white)
            font = pygame.font.SysFont('Comic Sans MS', 28, True, False)
            lock = pygame.font.SysFont('Comic Sans MS', 50, True, False)

            for row in range(4):
                inactive_color, background_color, active_color = PyGameBoard.convert_row_to_color(row)
                pygame.draw.rect(self.screen, background_color, [32, 32 + 126 * row, 1152, 118], 0)   # box behind the buttons
                for eyes in range(0, 11):
                    self.button(eyes, 80, 80, inactive_color, active_color)
                    text = font.render("{}".format(int(eyes + 2)), True, PyGameBoard.white)
                    if row < 2:
                        self.screen.blit(text, [80 + 92 * eyes, 126 * row + 70])
                    else:
                        self.screen.blit(text, [80 + 92 * (10 - eyes), 126 * row + 70])
                self.button(12, 72, 72, inactive_color, active_color, True)
                text = lock.render("*", True, PyGameBoard.white)
                self.screen.blit(text, [1102, 90 * (row + 1) + 36 * row - 30])

            pygame.draw.rect(self.screen, PyGameBoard.light_grey, [784, 536, 400, 60], 0)
            for eyes in range(1, 5):
                self.button(eyes, 40, 40, PyGameBoard.dark_grey, PyGameBoard.black)
            text = font.render("penalties", True, PyGameBoard.dark_grey)
            self.screen.blit(text, [800, 546])
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def button(self,eyes, w, h, inactive_color, active_color, circle=False):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        x, y = PyGameBoard.convert_eyes_to_coordinates(PyGameBoard.convert_color_to_row(active_color), eyes, circle)
        if click[0] == 0:
            self.mouse_down = False

        # choose color for button
        if PyGameBoard.is_mouse_over_button(x, y, w, h, circle, mouse):
            if circle:
                pygame.draw.circle(self.screen, active_color, [x, y], w // 2, 0)
            else:
                pygame.draw.rect(self.screen, active_color, (x, y, w, h))
            if click[0] == 1:
                self.click_button(x, active_color)
        else:   # choose color for button when the cursor isn't pointed at it
            eyes = PyGameBoard.convert_coordinates_to_eyes(active_color, x)
            if active_color == PyGameBoard.red_vibrant and eyes in self.crosses_red:
                inactive_color = active_color
            if active_color == PyGameBoard.yellow_vibrant and eyes in self.crosses_yellow:
                inactive_color = active_color
            if active_color == PyGameBoard.green_vibrant and eyes in self.crosses_green:
                inactive_color = active_color
            if active_color == PyGameBoard.blue_vibrant and eyes in self.crosses_blue:
                inactive_color = active_color
            if active_color == PyGameBoard.black and eyes <= self.penalties:
                inactive_color = active_color

            if circle:
                pygame.draw.circle(self.screen, inactive_color, [x, y], w // 2, 0)
            else:
                pygame.draw.rect(self.screen, inactive_color, (x, y, w, h))

    def click_button(self, x, active_color) -> bool:  # comparable to 'cross()'
        """sets a cross chosen by the player"""
        if self.mouse_down: return False
        self.mouse_down = True
        mouse = pygame.mouse.get_pos()
        row = active_color
        eyes = PyGameBoard.convert_coordinates_to_eyes(row, x)

        if eyes is not None:
            if row == PyGameBoard.red_vibrant:
                self.crosses_red.add(eyes)
            if row == PyGameBoard.yellow_vibrant:
                self.crosses_yellow.add(eyes)
            if row == PyGameBoard.green_vibrant:
                self.crosses_green.add(eyes)
            if row == PyGameBoard.blue_vibrant:
                self.crosses_blue.add(eyes)

        if row == PyGameBoard.black and eyes - 1 == self.penalties:
            self.penalties += 1

    @staticmethod
    def is_mouse_over_button(x, y, w, h, circle, mouse) -> bool:
        return (not circle and x < mouse[0] < x + w and y < mouse[1] < y + h) or \
                (circle and x - w / 2 < mouse[0] < x + w / 2 and y - h / 2 < mouse[1] < y + h / 2)

    @staticmethod
    def convert_coordinates_to_eyes(row, x):
        if row in (PyGameBoard.red_vibrant, PyGameBoard.yellow_vibrant):
            return ((x - 50) // 92) + 2  # + 2 because eyes in index from 0 -11 -> 2 - 13
        elif row in (PyGameBoard.green_vibrant, PyGameBoard.blue_vibrant):
            return 12 - ((x - 50) // 92)  # eyes originally in index from 0 -11 -> 12 - 1
        else:
            return (x - 930) // 50

    @staticmethod
    def convert_eyes_to_coordinates(row, eyes, circle):
        assert(row in range(5))
        if circle:
            return 1112, (90 * (row + 1) + 36 * row)
        if row < 2:
            return (50 + 92 * eyes), (50 * (row + 1) + 76 * row)    # x, y
        if row < 4:
            return (50 + 92 * (10 - eyes)), (50 * (row + 1) + 76 * row) # todo why 10 and not 12?
        return (930 + 50 * eyes), 546

    @staticmethod
    def convert_color_to_row(color):
        if color == PyGameBoard.red_vibrant:
            return 0
        if color == PyGameBoard.yellow_vibrant:
            return 1
        if color == PyGameBoard.green_vibrant:
            return 2
        if color == PyGameBoard.blue_vibrant:
            return 3
        if color == PyGameBoard.black:
            return 4

    @staticmethod
    def convert_row_to_color(row):
        # inactive, background, active
        if row == 0:
            return PyGameBoard.red, PyGameBoard.light_red, PyGameBoard.red_vibrant
        if row == 1:
            return PyGameBoard.yellow, PyGameBoard.light_yellow, PyGameBoard.yellow_vibrant
        if row == 2:
            return PyGameBoard.green, PyGameBoard.light_green, PyGameBoard.green_vibrant
        if row == 3:
            return PyGameBoard.blue, PyGameBoard.light_blue, PyGameBoard.blue_vibrant
        if row == 4:
            return PyGameBoard.light_grey, PyGameBoard.dark_grey, PyGameBoard.black

if __name__ == "__main__":
    board = PyGameBoard()
    board.show_background()

