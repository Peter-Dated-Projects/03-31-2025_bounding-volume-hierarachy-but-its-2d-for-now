import engine.context as ctx
import engine.constants as consts

from engine.system import ecs
from engine.system import world

from engine.physics import interact

import pygame


# ======================================================================== #
# AABB Collider
# ======================================================================== #


class AABBColliderComponent(interact.ShapeComponent):
    def __init__(self, width: float, height: float):
        super().__init__(
            [
                pygame.Vector2(-width / 2, -height / 2),
                pygame.Vector2(width / 2, -height / 2),
                pygame.Vector2(width / 2, height / 2),
                pygame.Vector2(-width / 2, height / 2),
            ],
        )

        self._rect = pygame.FRect(0, 0, width, height)

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def update(self):
        self._rect.center = self._entity._position

    def debug(self):
        pygame.draw.rect(consts.W_FRAMEBUFFER, (255, 0, 255), self._rect, 1)
