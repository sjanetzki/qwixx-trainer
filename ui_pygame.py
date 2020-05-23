from player import CrossPossibility
import pygame


class PyGameUi(object):

    pygame.init()

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
        self.is_mouse_down = False
        self.last_action = None
        self.crosses_by_color = [set(), set(), set(), set()]
        self.penalties = 0

    def show_background(self) -> None:
        """shows board as a with pygame functions"""
        pygame.display.set_caption("Qwixx Board")
        self.screen.fill(PyGameUi.white)
        font = pygame.font.SysFont('Comic Sans MS', 28, True, False)
        lock = pygame.font.SysFont('Comic Sans MS', 50, True, False)

        for row in range(4):
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    PyGameUi.close()
                    return
            inactive_color, background_color, active_color = PyGameUi.convert_row_to_color(row)
            pygame.draw.rect(self.screen, background_color, [32, 32 + 126 * row, 1152, 118],
                             0)  # box behind the buttons
            for eyes in range(0, 11):
                self.button(eyes, 80, 80, inactive_color, active_color)
                text = font.render("{}".format(int(eyes + 2)), True, PyGameUi.white)
                if row < 2:
                    self.screen.blit(text, [80 + 92 * eyes, 126 * row + 70])
                else:
                    self.screen.blit(text, [80 + 92 * (10 - eyes), 126 * row + 70])
            self.button(12, 72, 72, inactive_color, active_color, True)
            text = lock.render("*", True, PyGameUi.white)
            self.screen.blit(text, [1102, 90 * (row + 1) + 36 * row - 30])

        pygame.draw.rect(self.screen, PyGameUi.light_grey, [784, 536, 400, 60], 0)
        for eyes in range(1, 5):
            self.button(eyes, 40, 40, PyGameUi.dark_grey, PyGameUi.black)
        text = font.render("penalties", True, PyGameUi.dark_grey)
        self.screen.blit(text, [800, 546])
        clock = pygame.time.Clock()
        clock.tick(60)
        pygame.display.flip()

    def get_turn(self):
        while self.last_action is None:
            self.show_background()
        last_action = self.last_action
        self.last_action = None
        return last_action

    def button(self, eyes, w, h, inactive_color, active_color, circle=False):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        x, y = PyGameUi.convert_eyes_to_coordinates(PyGameUi.convert_color_to_row(active_color), eyes, circle)
        if click[0] == 0:
            self.is_mouse_down = False

        # choose color for button
        if PyGameUi.is_mouse_over_button(x, y, w, h, circle, mouse):
            if circle:
                pygame.draw.circle(self.screen, active_color, [x, y], w // 2, 0)
            else:
                pygame.draw.rect(self.screen, active_color, (x, y, w, h))
            if click[0] == 1:
                self.click_button(x, active_color)
        else:   # choose color for button when the cursor isn't pointed at it
            eyes = PyGameUi.convert_coordinates_to_eyes(active_color, x)
            if active_color == PyGameUi.red_vibrant and eyes in self.crosses_by_color[0]:
                inactive_color = active_color
            if active_color == PyGameUi.yellow_vibrant and eyes in self.crosses_by_color[1]:
                inactive_color = active_color
            if active_color == PyGameUi.green_vibrant and eyes in self.crosses_by_color[2]:
                inactive_color = active_color
            if active_color == PyGameUi.blue_vibrant and eyes in self.crosses_by_color[3]:
                inactive_color = active_color
            if active_color == PyGameUi.black and eyes <= self.penalties:
                inactive_color = active_color

            if circle:
                pygame.draw.circle(self.screen, inactive_color, [x, y], w // 2, 0)
            else:
                pygame.draw.rect(self.screen, inactive_color, (x, y, w, h))

    def click_button(self, x, active_color) -> bool:  # comparable to 'cross()'
        """sets a cross chosen by the player"""
        if self.is_mouse_down or self.last_action is not None:
            return False
        self.is_mouse_down = True
        row = active_color
        eyes = PyGameUi.convert_coordinates_to_eyes(row, x)

        if eyes is not None:
            if row == PyGameUi.red_vibrant:
                self.last_action = CrossPossibility(0, eyes)
            if row == PyGameUi.yellow_vibrant:
                self.last_action = CrossPossibility(1, eyes)
            if row == PyGameUi.green_vibrant:
                self.last_action = CrossPossibility(2, eyes)
            if row == PyGameUi.blue_vibrant:
                self.last_action = CrossPossibility(3, eyes)

        if row == PyGameUi.black and eyes - 1 == self.penalties:
            self.last_action = CrossPossibility(4, None)

    @staticmethod
    def close():
        pygame.quit()

    @staticmethod
    def is_mouse_over_button(x, y, w, h, circle, mouse) -> bool:
        return (not circle and x < mouse[0] < x + w and y < mouse[1] < y + h) or \
                (circle and x - w / 2 < mouse[0] < x + w / 2 and y - h / 2 < mouse[1] < y + h / 2)

    @staticmethod
    def convert_coordinates_to_eyes(row, x):
        if row in (PyGameUi.red_vibrant, PyGameUi.yellow_vibrant):
            return ((x - 50) // 92) + 2  # + 2 because eyes in index from 0 -11 -> 2 - 13
        elif row in (PyGameUi.green_vibrant, PyGameUi.blue_vibrant):
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
        if color == PyGameUi.red_vibrant:
            return 0
        if color == PyGameUi.yellow_vibrant:
            return 1
        if color == PyGameUi.green_vibrant:
            return 2
        if color == PyGameUi.blue_vibrant:
            return 3
        if color == PyGameUi.black:
            return 4

    @staticmethod
    def convert_row_to_color(row):
        # inactive, background, active
        if row == 0:
            return PyGameUi.red, PyGameUi.light_red, PyGameUi.red_vibrant
        if row == 1:
            return PyGameUi.yellow, PyGameUi.light_yellow, PyGameUi.yellow_vibrant
        if row == 2:
            return PyGameUi.green, PyGameUi.light_green, PyGameUi.green_vibrant
        if row == 3:
            return PyGameUi.blue, PyGameUi.light_blue, PyGameUi.blue_vibrant
        if row == 4:
            return PyGameUi.light_grey, PyGameUi.dark_grey, PyGameUi.black


if __name__ == "__main__":
    pygame_board = PyGameUi()
    pygame_board.show_background()
