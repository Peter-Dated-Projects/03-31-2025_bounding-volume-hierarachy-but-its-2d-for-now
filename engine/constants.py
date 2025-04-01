import glm
import pygame


# ======================================================================== #
# context
# ======================================================================== #

ENGINE_NAME = "SORAGL"

# all static data and objects
# singleton for main engine data

RUNNING = False
DEBUG_MODE = False

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Paint Gun Rogue-Lite"
WINDOW_FPS = 60
WINDOW_BIT_DEPTH = 32
WINDOW_FLAGS = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
WINDOW_ICON = "assets/icon.png"

# opengl / moderngl objects
FRAMEBUFFER_FLAGS = pygame.SRCALPHA
FRAMEBUFFER_BIT_DEPTH = 32
FRAMEBUFFER_WIDTH = 1280
FRAMEBUFFER_HEIGHT = 720

MGL_CONTEXT = None
MGL_FRAMEBUFFER = None
MGL_FRAMEBUFFER_VAO = None
MGL_FRAMEBUFFER_VBO = None
MGL_FRAMEBUFFER_SHADER = None
MGL_FRAMEBUFFER_RENDERING_MANIFOLD = None

BACKGROUND_COLOR = (255, 0, 0)

# pygame objects
W_FRAMEBUFFER = None
W_SURFACE = None
W_CLOCK = None

# time
DELTA_TIME = 0
START_TIME = 0
END_TIME = 0
RUN_TIME = 0

# objects
CTX_WINDOW = None
CTX_ECS_HANDLER = None
CTX_INPUT_HANDLER = None
CTX_SIGNAL_HANDLER = None
CTX_RESOURCE_MANAGER = None
CTX_GAMESTATE_MANAGER = None

# world constants
DEFAULT_CHUNK_PIXEL_WIDTH = 4096
DEFAULT_CHUNK_PIXEL_HEIGHT = 4096

DEFAULT_PHYSICS_GRAVITY = pygame.Vector2(0, -9.8)
DEFAULT_PHYSICS_POS_STEPS = 2
DEFAULT_PHYSICS_VEL_STEPS = 4


# ======================================================================== #
# constants
# ======================================================================== #


class Constants:

    UP = pygame.Vector2(0, -1)
    DOWN = pygame.Vector2(0, 1)
    LEFT = pygame.Vector2(-1, 0)
    RIGHT = pygame.Vector2(1, 0)

    GRAVITY_VECTOR = DOWN * 9.8


class GLM_Constants:

    UP = glm.vec3(0, 1, 0)
    DOWN = glm.vec3(0, -1, 0)
    RIGHT = glm.vec3(1, 0, 0)
    LEFT = glm.vec3(-1, 0, 0)
    FORWARD = glm.vec3(0, 0, 1)
    BACKWARD = glm.vec3(0, 0, -1)

    ORIGIN = glm.vec3(0, 0, 0)
