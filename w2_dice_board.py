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
            font = pygame.font.SysFont('letters for learners', 36, True, False)
            lock = pygame.font.SysFont('letters for learners', 64, True, False)

            pygame.draw.rect(self.screen, PyGameBoard.light_red, [32, 32, 1152, 118], 0)   # box behind the fields
            for field in range(0, 11):
                self.button(50 + 92 * field, 50, 80, 80, PyGameBoard.red, PyGameBoard.red_vibrant)
                text = font.render("{}".format(int(field + 2)), True, PyGameBoard.white)
                self.screen.blit(text, [80 + 92 * field, 70])
            self.button(1112, 90, 72, 72, PyGameBoard.red, PyGameBoard.red_vibrant, True)

            pygame.draw.rect(self.screen, PyGameBoard.light_yellow, [32, 158, 1152, 118], 0)
            for field in range(0, 11):
                self.button(50 + 92 * field, 50 * 2 + 76, 80, 80, PyGameBoard.yellow, PyGameBoard.yellow_vibrant)
                text = font.render("{}".format(int(field + 2)), True, PyGameBoard.white)
                self.screen.blit(text, [80 + 92 * field, 70 * 2 + 56])
            self.button(1112, 90 * 2 + 36, 72, 72, PyGameBoard.yellow, PyGameBoard.yellow_vibrant, True)

            pygame.draw.rect(self.screen, PyGameBoard.light_green, [32, 284, 1152, 118], 0)
            for field in range(0, 11):
                self.button(50 + 92 * field, 50 * 3 + 76 * 2, 80, 80, PyGameBoard.green, PyGameBoard.green_vibrant)
                text = font.render("{}".format(int(12 - field)), True, PyGameBoard.white)
                self.screen.blit(text, [80 + 92 * field, 70 * 3 + 56 * 2])
            self.button(1112, 90 * 3 + 36 * 2, 72, 72, PyGameBoard.green, PyGameBoard.green_vibrant, True)

            pygame.draw.rect(self.screen, PyGameBoard.light_blue, [32, 410, 1152, 118], 0)
            for field in range(0, 11):
                self.button(50 + 92 * field, 50 * 4 + 76 * 3, 80, 80, PyGameBoard.blue, PyGameBoard.blue_vibrant)
                text = font.render("{}".format(int(12 - field)), True, PyGameBoard.white)
                self.screen.blit(text, [80 + 92 * field, 70 * 4 + 56 * 3])
            self.button(1112, 90 * 4 + 36 * 3, 72, 72, PyGameBoard.blue, PyGameBoard.blue_vibrant,True)

            for row in range(4):
                text = lock.render("*", True, PyGameBoard.white)
                self.screen.blit(text, [1102, 90 * (row + 1) + 36 * row - 30])

            pygame.draw.rect(self.screen, PyGameBoard.light_grey, [784, 536, 400, 60], 0)
            for field in range(1, 5):
                self.button(970 + 10 * field + 40 * (field - 1), 546, 40, 40, PyGameBoard.dark_grey, PyGameBoard.black)
            text = font.render("penalties", True, PyGameBoard.dark_grey)
            self.screen.blit(text, [800, 546])
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def button(self, x, y, w, h, inactive_color, active_color, circle=False):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
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
            if active_color == PyGameBoard.black and eyes < self.penalties:
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

        if row == PyGameBoard.black and eyes == self.penalties:
            self.penalties += 1

    @staticmethod
    def is_mouse_over_button(x, y, w, h, circle, mouse) -> bool:
        return (not circle and x < mouse[0] < x + w and y < mouse[1] < y + h) or \
                (circle and x - w / 2 < mouse[0] < x + w / 2 and y - h / 2 < mouse[1] < y + h / 2)

    @staticmethod
    def convert_coordinates_to_eyes(row, x):
        eyes = None
        if row in (PyGameBoard.red_vibrant, PyGameBoard.yellow_vibrant):
            eyes = ((x - 50) // 92) + 2  # + 2 because fields in index form 0 -11 -> 2 - 13
        elif row in (PyGameBoard.green_vibrant, PyGameBoard.blue_vibrant):
            eyes = 12 - ((x - 50) // 92)  # fields originally in index form 0 -11 -> 12 - 1
        else:
            eyes = ((x - 970) // 50)
        return eyes

if __name__ == "__main__":
    board = PyGameBoard()
    board.show_background()

