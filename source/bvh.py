import pygame

# ------------------------------------------------------------------------ #
# bvh class
# ------------------------------------------------------------------------ #


class BVHContainer2D:
    PARTITION_COUNT = 4

    def __init__(
        self, world_area: pygame.FRect, max_depth: int = 2, objects: list = []
    ):
        self._world_area = world_area
        self._max_depth = max_depth

        self._root = self.construct(objects, world_area, 0)

    # ---------------------------------------------------- #
    # properties
    # ---------------------------------------------------- #

    def update(self, objects):
        """
        Update the BVH tree with a new list of objects.
        """
        self._root = self.construct(objects, self._world_area, 0)

    def construct(self, objects: list, world_area: pygame.FRect, depth: int):
        """
        Construct the BVH tree from a list of objects.
        """

        result = BVHNode2D(world_area, pygame.FRect(world_area.center, (0, 0)), depth)

        # determine if need to create child nodes
        if depth < self._max_depth:

            # partition current area into 4 sections
            _width = world_area.width / 2
            _height = world_area.height / 2
            areas = [
                pygame.FRect(world_area.x, world_area.y, _width, _height),  # top-left
                pygame.FRect(
                    world_area.x + _width, world_area.y, _width, _height
                ),  # top-right
                pygame.FRect(
                    world_area.x, world_area.y + _height, _width, _height
                ),  # bottom-left
                pygame.FRect(
                    world_area.x + _width, world_area.y + _height, _width, _height
                ),  # bottom-right
            ]

            children = [
                self.construct(
                    [o for o in objects if areas[0].collidepoint(o._position)],
                    areas[0],
                    depth + 1,
                ),
                self.construct(
                    [o for o in objects if areas[1].collidepoint(o._position)],
                    areas[1],
                    depth + 1,
                ),
                self.construct(
                    [o for o in objects if areas[2].collidepoint(o._position)],
                    areas[2],
                    depth + 1,
                ),
                self.construct(
                    [o for o in objects if areas[3].collidepoint(o._position)],
                    areas[3],
                    depth + 1,
                ),
            ]

            result._children = children
            for c in children:
                # set parent
                c._parent = result
                result._bounding_area.union_ip(c._bounding_area)
                result._object_count += c._object_count

        else:
            # if depth is max, we need to do math
            # calculate bounding area by determining the max and min of all objects
            _max = [world_area.x, world_area.y]
            _min = [world_area.right, world_area.bottom]
            # if no objects, return empty
            for o in objects:
                _min[0] = min(_min[0], o._position.x)
                _min[1] = min(_min[1], o._position.y)
                _max[0] = max(_max[0], o._position.x)
                _max[1] = max(_max[1], o._position.y)

            # if no objects, return empty
            if _min[0] == _max[0] and _min[1] == _max[1]:
                _min = [0, 0]
                _max = [0, 0]

            result._bounding_area = pygame.FRect(
                _min[0],
                _min[1],
                _max[0] - _min[0],
                _max[1] - _min[1],
            )

            result._objects = objects
            result._object_count = len(objects)
            result._depth = depth
            result._parent = None

        # print(f"Bounding Area: {result._bounding_area}")
        # return result
        return result

    def draw(self, surface, only_leaf: bool = False):
        """
        Draw the BVH tree.
        """
        self._root.draw(surface, None, only_leaf=only_leaf)


# ------------------------------------------------------------------------ #
# bvh node
# ------------------------------------------------------------------------ #


class BVHNode2D:
    def __init__(
        self,
        world_area: pygame.FRect,
        bounding_area: pygame.FRect,
        depth: int,
        parent=None,
    ):
        # the total world area the bvh covers
        self._world_area = world_area

        # the bounding area of this node -- dictated by child objects
        self._bounding_area = bounding_area

        # depth + parent
        self._depth = depth
        self._parent = parent

        # children
        self._children = []

        # objects
        self._objects = []
        self._object_count = 0

    def draw(self, surface, color: tuple, only_leaf: bool = False):
        """
        Draw the BVH node.
        """
        if color is None:
            color = (255, 0, 0, 10)

        # draw children
        for child in self._children:
            child.draw(
                surface,
                color=(
                    color[0],
                    color[1] + self._depth * 40,
                    color[2],
                    color[3] + 20,
                ),
                only_leaf=only_leaf,
            )

        if (
            not only_leaf or (only_leaf and not self._children)
        ) and self._object_count > 0:
            # draw bounding area
            pygame.draw.rect(
                surface,
                (color[0], color[1], color[2], color[3]),
                self._bounding_area,
                1,
            )
