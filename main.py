import os
import sys

if not os.environ.get("PYTHONHASHSEED"):
    os.environ["PYTHONHASHSEED"] = "13"

    import subprocess

    subprocess.run([sys.executable] + sys.argv)
    sys.exit()

# ======================================================================== #
# setup
# ======================================================================== #

import pygame

import engine.context as ctx
import engine.constants as consts

# ------------------------------------------------------------------------ #


consts.WINDOW_WIDTH = 1280
consts.WINDOW_HEIGHT = 720
consts.WINDOW_TITLE = "Boids"
consts.WINDOW_FPS = 60
consts.WINDOW_FLAGS = (
    pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.OPENGL
)
consts.WINDOW_ICON = None
consts.BACKGROUND_COLOR = (255, 224, 169)

# consts.FRAMEBUFFER_WIDTH = 1280 // 2
# consts.FRAMEBUFFER_HEIGHT = 720 // 2
consts.FRAMEBUFFER_WIDTH = 500
consts.FRAMEBUFFER_HEIGHT = 500
consts.FRAMEBUFFER_FLAGS = pygame.SRCALPHA
consts.FRAMEBUFFER_BIT_DEPTH = 32

consts.DEBUG_MODE = True

ctx.init()

# ======================================================================== #
# loading resources
# ======================================================================== #

from source import boid

for i in range(10):
    consts.CTX_WORLD.add_entity(boid.Boid(f"boid-{i}"))


# ======================================================================== #
# run game
# ======================================================================== #


ctx.run()
