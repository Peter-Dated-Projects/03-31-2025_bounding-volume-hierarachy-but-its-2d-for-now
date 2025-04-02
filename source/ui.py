import pygame

# ------------------------------------------------------------------------ #
# ui
# ------------------------------------------------------------------------ #


class UI:
    def __init__(self, ui_rect: pygame.FRect, config: dict = None):
        self._ui_rect = ui_rect
        self._ui_elements = []

        self._config = (
            config
            if config
            else {
                "font": "Arial",
                "font_size": 12,
            }
        )

    def add_element(self, element):
        self._ui_elements.append(element)

    def draw(self, surface):
        for element in self._ui_elements:
            element.draw(surface, self)


class UIObject:
    def __init__(self, relative_rect: pygame.FRect = None):
        self._relative_rect = relative_rect

    def draw(self, surface, ctx):
        pass


# ------------------------------------------------------------------------ #
# ui slider
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
# ui label
# ------------------------------------------------------------------------ #
class UILabel(UIObject):
    def __init__(self, relative_rect: pygame.FRect = None, text: str = ""):
        super().__init__(relative_rect)
        self._relative_rect = relative_rect
        self._text = text
