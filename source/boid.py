import pygame
import uuid

# ------------------------------------------------------------------------ #
# boid class
# ------------------------------------------------------------------------ #


class Boid:
    """
    Boid -- a single flight object

    This class represents a single boid in the simulation. It contains
    properties such as position, velocity, and acceleration. It also
    contains methods for updating the boid's position and velocity based
    on the rules of flocking behavior.

    The boid
    - is non-collideable
    - has a color
    - has a position
    - has a velocity
    - has an acceleration

    """

    def __init__(self):
        self._id = uuid.uuid4()
        self._position = pygame.Vector2()
        self._velocity = pygame.Vector2()
        self._acceleration = pygame.Vector2()
        self._color = (255, 255, 255)

        self._push = pygame.Vector2()
        self._steer = pygame.Vector2()
        self._cohesion = pygame.Vector2()
