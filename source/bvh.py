import pygame

# ------------------------------------------------------------------------ #
# bvh class
# ------------------------------------------------------------------------ #


class BVHContainer2D:
    def __init__(self, world_area: pygame.FRect, depth: int = 2):
        self._world_area = world_area
        self._depth = depth

    def construct(self, objects: list):
        """
        Construct the BVH tree from a list of objects.
        """
        self._objects = objects
        self._root = BVHNode2D(self._world_area, self._world_area)


# ------------------------------------------------------------------------ #
# bvh node
# ------------------------------------------------------------------------ #


class BVHNode2D:
    def __init__(
        self, world_area: pygame.FRect, bounding_area: pygame.FRect, parent=None
    ):
        pass
