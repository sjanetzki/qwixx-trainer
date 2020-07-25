from player import CrossPossibility
import pygame


class PyGameUi(object):

    pygame.init()

    scale_factor = 2/3

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

    screen_x_length = int(1216 * scale_factor)
    screen_y_length = int(650 * scale_factor)
    box_x = int(32 * scale_factor)
    box_y = box_x
    box_y_distance = int(126 * scale_factor)
    box_x_length = int(1152 * scale_factor)
    box_y_length = int(118 * scale_factor)
    button_length = int(80 * scale_factor)
    button_x_distance = int(92 * scale_factor)
    button_y = int(50 * scale_factor)
    button_x = button_y
    button_text_y = int(70 * scale_factor)
    circle_diameter = int(72 * scale_factor)
    circle_radius = circle_diameter // 2
    circle_x = int(1112 * scale_factor)
    circle_text_x_offset = int(-10 * scale_factor)
    circle_y = int(90 * scale_factor)
    circle_text_y_offset = int(6 * scale_factor)
    penalty_box_x = int(784 * scale_factor)
    penalty_box_y = (536 * scale_factor)
    penalty_box_x_length = int(400 * scale_factor)
    penalty_box_y_length = int(60 * scale_factor)
    penalty_button_length = button_length // 2
    penalty_button_x_offset = int(146 * scale_factor)
    penalty_text_x_offset = int(16 * scale_factor)
    penalty_text_y_offset = (penalty_box_y_length - penalty_button_length) // 2
    skip_button_x = int(590 * scale_factor)
    skip_button_x_length = int(170 * scale_factor)
    dice_text_x_offset = int(225 * scale_factor)
    dice_text_y_offset = int(40 * scale_factor)
    player_mode_x_offset = int(205 * scale_factor)
    player_mode_y_offset = dice_text_y_offset * 2
    font_numbers_size = int(28 * scale_factor)
    font_lock_size = int(50 * scale_factor)

    def __init__(self):
        size = (PyGameUi.screen_x_length, PyGameUi.screen_y_length)
        self.screen = pygame.display.set_mode(size)
        self.is_mouse_down = False
        self.last_action = None
        self.crosses_by_color = [set(), set(), set(), set()]
        self.penalties = 0
        self.lst_eyes = [0, 0, 0, 0, 0, 0]
        self.is_turn_invalid = False
        self.is_active_player = True

    def show_background(self) -> None:
        """shows board as a with pygame functions"""
        pygame.display.set_caption("Qwixx Board")
        if self.is_turn_invalid:
            self.screen.fill(PyGameUi.red_vibrant)
        else:
            self.screen.fill(PyGameUi.white)

        font = pygame.font.SysFont('Comic Sans MS', PyGameUi.font_numbers_size, True, False)
        lock = pygame.font.SysFont('Comic Sans MS', PyGameUi.font_lock_size, True, False)

        for row in range(4):
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    PyGameUi.close()
                    return
            inactive_color, background_color, active_color = PyGameUi.convert_number_to_color(row)
            pygame.draw.rect(self.screen, background_color,
                             [PyGameUi.box_x, PyGameUi.box_y + PyGameUi.box_y_distance * row, PyGameUi.box_x_length,
                              PyGameUi.box_y_length], 0)  # box behind the buttons
            for eyes in range(0, 11):
                self.button(eyes, PyGameUi.button_length, PyGameUi.button_length, inactive_color, active_color)
                text = font.render("{}".format(int(eyes + 2)), True, PyGameUi.white)
                if row < 2:
                    self.screen.blit(text, [PyGameUi.button_length + PyGameUi.button_x_distance * eyes,
                                            PyGameUi.box_y_distance * row + PyGameUi.button_text_y])
                else:
                    self.screen.blit(text, [PyGameUi.button_length + PyGameUi.button_x_distance * (10 - eyes),
                                            PyGameUi.box_y_distance * row + PyGameUi.button_text_y])
            self.button(12, PyGameUi.circle_diameter, PyGameUi.circle_diameter, inactive_color, active_color, True)
            text = lock.render("*", True, PyGameUi.white)
            self.screen.blit(text, [PyGameUi.circle_x + PyGameUi.circle_text_x_offset,
                                    PyGameUi.circle_y * (row + 1) + PyGameUi.circle_radius * (
                                                row - 1) + PyGameUi.circle_text_y_offset])

        # draw penalties
        pygame.draw.rect(self.screen, PyGameUi.light_grey,
                         [PyGameUi.penalty_box_x, PyGameUi.penalty_box_y, PyGameUi.penalty_box_x_length,
                          PyGameUi.penalty_box_y_length], 0)
        for eyes in range(1, 5):
            self.button(eyes, PyGameUi.penalty_button_length, PyGameUi.penalty_button_length, PyGameUi.dark_grey,
                        PyGameUi.black)
        text = font.render("penalties", True, PyGameUi.dark_grey)
        self.screen.blit(text, [PyGameUi.penalty_box_x + PyGameUi.penalty_text_x_offset,
                                PyGameUi.penalty_box_y + PyGameUi.penalty_text_y_offset])

        pygame.draw.rect(self.screen, PyGameUi.light_grey,
                         [PyGameUi.skip_button_x, PyGameUi.penalty_box_y, PyGameUi.skip_button_x_length,
                          PyGameUi.penalty_box_y_length], 0)
        # self.button(0, 50, 20, PyGameUi.light_grey, PyGameUi.dark_grey) # todo
        text = font.render("skip 2nd x", True, PyGameUi.dark_grey)
        self.screen.blit(text, [PyGameUi.skip_button_x + PyGameUi.penalty_text_y_offset,
                                PyGameUi.penalty_box_y + PyGameUi.penalty_text_y_offset])

        self._render_dice(font)
        self._show_player_mode(font)

        clock = pygame.time.Clock()
        clock.tick(60)
        pygame.display.flip()

    def _render_dice(self, font):
        for dice in range(len(self.lst_eyes)):
            text = font.render("{}".format(self.lst_eyes[dice]), True, self.convert_number_to_color(dice, True))
            self.screen.blit(text,
                             [PyGameUi.button_length + PyGameUi.button_x_distance * dice,
                              PyGameUi.penalty_box_y + PyGameUi.penalty_text_y_offset])

        text = font.render("your dice", True, PyGameUi.dark_grey)
        self.screen.blit(text, [PyGameUi.box_x + PyGameUi.dice_text_x_offset,
                                PyGameUi.penalty_box_y + PyGameUi.dice_text_y_offset])

    def _show_player_mode(self, font):
        if self.is_active_player:
            player_mode = "active player"
        else:
            player_mode = "passive player"
        text = font.render("{}".format(player_mode), True, PyGameUi.dark_grey)
        self.screen.blit(text, [PyGameUi.box_x + PyGameUi.player_mode_x_offset,
                                PyGameUi.penalty_box_y + PyGameUi.player_mode_y_offset])

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
        self.is_turn_invalid = False
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
            return (x - PyGameUi.button_x) // PyGameUi.button_x_distance + 2  # + 2 because eyes in index from 0 -11 -> 2 - 13
        elif row in (PyGameUi.green_vibrant, PyGameUi.blue_vibrant):
            return 12 - ((x - PyGameUi.button_x) // PyGameUi.button_x_distance)  # eyes originally in index from 0 -11 -> 12 - 1
        else:  # penalties
            return (x - PyGameUi.penalty_box_x - PyGameUi.penalty_button_x_offset) // (
                        PyGameUi.penalty_button_length + PyGameUi.penalty_text_y_offset)

    @staticmethod
    def convert_eyes_to_coordinates(row, eyes, circle):
        assert (row in range(5))
        if circle:
            return (PyGameUi.circle_x, PyGameUi.circle_y * (row + 1) + PyGameUi.circle_radius * row)
        if row < 2:
            return (PyGameUi.button_x + PyGameUi.button_x_distance * eyes,
                    PyGameUi.button_y * (row + 1) + (PyGameUi.box_y_distance - PyGameUi.button_y) * row)  # x, y
        if row < 4:
            return (PyGameUi.button_x + PyGameUi.button_x_distance * (10 - eyes)), (PyGameUi.button_y * (row + 1) + (
                    PyGameUi.box_y_distance - PyGameUi.button_y) * row)  # todo why 10 and not 12?
        return (PyGameUi.penalty_box_x + PyGameUi.penalty_button_x_offset + (
                PyGameUi.penalty_button_length + PyGameUi.penalty_text_y_offset) * eyes,
                PyGameUi.penalty_box_y + PyGameUi.penalty_text_y_offset)

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
    def convert_number_to_color(number, is_dice=False):
        if is_dice:
            if number in (0, 1):
                return PyGameUi.dark_grey
            if number == 2:
                return PyGameUi.red
            if number == 3:
                return PyGameUi.yellow_vibrant
            if number == 4:
                return PyGameUi.green_vibrant
            if number == 5:
                return PyGameUi.blue_vibrant
        else:   # inactive, background, active
            if number == 0:
                return PyGameUi.red, PyGameUi.light_red, PyGameUi.red_vibrant
            if number == 1:
                return PyGameUi.yellow, PyGameUi.light_yellow, PyGameUi.yellow_vibrant
            if number == 2:
                return PyGameUi.green, PyGameUi.light_green, PyGameUi.green_vibrant
            if number == 3:
                return PyGameUi.blue, PyGameUi.light_blue, PyGameUi.blue_vibrant
            if number == 4:
                return PyGameUi.light_grey, PyGameUi.dark_grey, PyGameUi.black


if __name__ == "__main__":
    pygame_board = PyGameUi()
    pygame_board.show_background()
