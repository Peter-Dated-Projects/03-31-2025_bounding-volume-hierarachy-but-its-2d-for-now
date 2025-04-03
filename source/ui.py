import pygame

# ------------------------------------------------------------------------ #
# ui
# ------------------------------------------------------------------------ #


class UI:
    def __init__(self, ui_rect: pygame.FRect, config: dict = None):
        self._ui_rect = ui_rect
        self._ui_elements = []
        self._visible = True

        self._config = (
            config
            if config
            else {
                "font": "Arial",
                "font_size": 18,
            }
        )

        pygame.font.init()

        # load font
        self._font = pygame.font.Font(
            pygame.font.match_font(self._config["font"]),
            self._config["font_size"],
        )
        self._font.set_bold(True)

    def add_element(self, element):
        self._ui_elements.append(element)

    def draw(self, surface):
        if not self._visible:
            return
        for element in self._ui_elements:
            element.draw(surface, self)

    def calculate_absolute_rect(self, child_rect: pygame.FRect):
        # calculate absolute rect
        absolute_rect = pygame.FRect(
            self._ui_rect.x + child_rect.x,
            self._ui_rect.y + child_rect.y,
            child_rect.width,
            child_rect.height,
        )
        return absolute_rect


class UIObject:
    def __init__(self, relative_rect: pygame.FRect = None):
        self._relative_rect = relative_rect

    def draw(self, surface, ctx):
        pass


# ------------------------------------------------------------------------ #
# ui slider
# ------------------------------------------------------------------------ #


class UISlider(UIObject):
    def __init__(
        self,
        relative_rect: pygame.FRect,
        min_value: float,
        max_value: float,
        default_value: float,
        update_func: callable = None,
    ):
        """
        Initialize the slider.
        :param relative_rect: The slider's rectangle relative to its container.
        :param min_value: The minimum slider value.
        :param max_value: The maximum slider value.
        :param default_value: The starting value.
        """
        super().__init__(relative_rect)
        self._relative_rect = relative_rect
        self._min_value = min_value
        self._max_value = max_value
        self._value = default_value
        self._dragging = False
        self._knob_width = 10  # Width of the slider knob in pixels
        self._update_func = update_func

    def draw(self, surface, ctx):
        """
        Draw the slider track and knob, and update the slider value if the user is dragging.
        :param surface: The surface to draw on.
        :param ctx: The UI context, which provides methods like calculate_absolute_rect and font.
        """
        # Get the absolute position and size of the slider track
        slider_rect = ctx.calculate_absolute_rect(self._relative_rect)

        # Draw the slider track (background)
        pygame.draw.rect(surface, (100, 100, 100), slider_rect)

        # Calculate the knob position based on the current value.
        fraction = (self._value - self._min_value) / (self._max_value - self._min_value)
        knob_x = slider_rect.x + fraction * slider_rect.width
        knob_rect = pygame.FRect(
            knob_x - self._knob_width / 2,
            slider_rect.y,
            self._knob_width,
            slider_rect.height,
        )

        # Draw the knob
        pygame.draw.rect(surface, (255, 255, 255), knob_rect)

        # Handle mouse interaction
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pressed:
            # If the mouse is pressed and either within the slider track or already dragging
            if slider_rect.collidepoint(mouse_pos) or self._dragging:
                self._dragging = True
                # Calculate local x-coordinate within the slider track
                local_x = mouse_pos[0] - slider_rect.x
                # Determine fraction of the slider track traversed (clamp between 0 and 1)
                fraction = max(0, min(1, local_x / slider_rect.width))
                # Update the slider's value based on the fraction of track
                self._value = self._min_value + fraction * (
                    self._max_value - self._min_value
                )
        else:
            self._dragging = False

        # Call the update function if provided
        if self._update_func:
            self._update_func(self._value)

    def get_current_value(self):
        """
        Return the current value of the slider.
        """
        return self._value


# ------------------------------------------------------------------------ #
# ui label
# ------------------------------------------------------------------------ #
class UILabel(UIObject):
    def __init__(self, relative_rect: pygame.FRect = None, text: str = ""):
        super().__init__(relative_rect)
        self._relative_rect = relative_rect
        self._text = text

    def draw(self, surface, ctx):
        # draw text
        text_surface = ctx._font.render(self._text, True, (255, 255, 255))
        text_rect = ctx.calculate_absolute_rect(self._relative_rect)
        surface.blit(text_surface, text_rect)


# -------------------------------------------------------------------------- #
# ui button
# -------------------------------------------------------------------------- #


class UIButton(UIObject):
    def __init__(
        self,
        relative_rect: pygame.FRect = None,
        onclick: callable = None,
        default_value: bool = False,
    ):
        super().__init__(relative_rect)
        self._relative_rect = relative_rect
        self._onclick = onclick
        self._clicked = False
        self._value = default_value

    def draw(self, surface, ctx):
        # draw button
        button_rect = ctx.calculate_absolute_rect(self._relative_rect)
        pygame.draw.rect(
            surface, (0, 255, 0) if self._value else (255, 0, 0), button_rect
        )

        # on click handling
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if button_rect.collidepoint(mouse_pos):
            if mouse_buttons[0]:
                if not self._clicked:
                    self._clicked = True
                    self._value = not self._value
                    # call onclick function
                    if self._onclick:
                        self._onclick()
        else:
            self._clicked = False
