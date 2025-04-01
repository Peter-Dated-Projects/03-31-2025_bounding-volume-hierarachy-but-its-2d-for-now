import pygame

import engine.context as ctx
import engine.constants as consts

from engine.io import resourcemanager
from engine.system import ecs


# ======================================================================== #
# Sprite
# ======================================================================== #


class SpriteComponent(ecs.Component):
    def __init__(
        self, image: pygame.Surface = None, filepath: str = None, rm_uuid: str = None
    ):
        """
        Sprite Component

        image: pygame.Surface -- the actual visual
        filepath: str -- the path to the image file
        rm_uuid: str -- {path}||{frame number or other unique identifier}
        """
        super().__init__()

        self._extra["offset"] = (0, 0)

        # check if empty sprite provided
        if image is None and filepath is None and rm_uuid is None:
            # leave as empty sprite
            self._image = pygame.Surface((0, 0))
            self._filepath = None
            self._rm_uuid = None
            self._rect = self._image.get_rect()
            self._spritesheet = None
            self._flipped = False

            return

        self._image = (
            image if image is not None else consts.CTX_RESOURCE_MANAGER.load(filepath)
        )
        self._filepath = filepath
        self._rm_uuid = rm_uuid if rm_uuid is not None else filepath
        self._rect = self._image.get_rect()
        self._flipped = False

        # optional spritesheet
        self._spritesheet = None

    def __post_init__(self):
        # try to center sprite
        self._rect.center = self._entity._position

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def update(self):
        self._rect.center = self._entity._position

    def get_image(self):
        return self._image

    def get_rm_uuid(self):
        return self._rm_uuid

    def get_source_image(self):
        # sprite rm_uuids are stored as: f"{image path}||{frame number}"
        return resourcemanager.load(self._rm_uuid.split("||")[0])

    def get_rect(self):
        return self._rect

    # ------------------------------------------------------------------------ #
    # special methods
    # ------------------------------------------------------------------------ #

    def __str__(self):
        return f"Sprite(name={self._name})"


# ======================================================================== #
# Sprite Renderer Component
# ======================================================================== #


class SpriteRendererComponent(ecs.Component):
    def __init__(self, target: SpriteComponent = None):
        super().__init__()
        self._target = target
        self._target_comp = None

    def __post_init__(self):
        if self._target is not None:
            self._target_comp = self._entity.get_component_by_id(self._target._uuid)
        else:
            self._target_comp = self._entity.get_components(SpriteComponent)
            if len(self._target_comp) == 0:
                print("No SpriteComponent found in entity. Cannot render sprite.")
                self._target_comp = None
            else:
                self._target_comp = self._target_comp[0]

    # ------------------------------------------------------------------------ #
    # component logic
    # ------------------------------------------------------------------------ #

    def update(self):
        consts.W_FRAMEBUFFER.blit(
            pygame.transform.flip(
                self._target_comp._image, self._target_comp._flipped, False
            ),
            self._target_comp._rect.topleft,
        )

    def debug(self):
        pygame.draw.rect(consts.W_FRAMEBUFFER, (200, 0, 0), self._target_comp._rect, 1)
