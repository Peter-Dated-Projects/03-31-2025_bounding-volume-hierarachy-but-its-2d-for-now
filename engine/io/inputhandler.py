import pygame

# ======================================================================== #
# Input handler
# ======================================================================== #


class InputHandler:

    KEYBOARD_INPUTS = {}
    MOUSE_INPUTS = {}

    # ------------------------------------------------------------------------ #
    # keyboard
    # ------------------------------------------------------------------------ #

    @classmethod
    def update(cls):
        cls.KEYBOARD_INPUTS = pygame.key.get_pressed()
        cls.MOUSE_INPUTS = pygame.mouse.get_pressed()

    @classmethod
    def get_keyboard_pressed(cls, key: int):
        return cls.KEYBOARD_INPUTS[key]

    @classmethod
    def get_mouse_pressed(cls, button: int):
        return cls.MOUSE_INPUTS[button]
