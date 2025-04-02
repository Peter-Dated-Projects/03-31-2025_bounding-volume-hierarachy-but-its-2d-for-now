import time
import pygame
import random
import colorsys
import pygame_gui

from source import boid

# ------------------------------------------------------------------------ #
# setup
# ------------------------------------------------------------------------ #

# constants
W_RUNNING = False
W_SIZE = [1280, 720]
W_FB_SIZE = [1280, 720]
W_FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SRCALPHA
W_BIT_DEPTH = 32
W_BACKGROUND_COLOR = (0, 17, 41, 255)
W_CLOCK = pygame.time.Clock()

W_BUF_SIZE = (W_SIZE[0] * 1.03, W_SIZE[1] * 1.03)
W_BUF_POS = (-(W_BUF_SIZE[0] - W_SIZE[0]) // 2, -(W_BUF_SIZE[1] - W_SIZE[1]) // 2)

W_DELTA = 1 / 60
W_FPS = 60

# surfaces
W_WINDOW = pygame.display.set_mode(W_SIZE, W_FLAGS, W_BIT_DEPTH)
W_FRAMEBUFFER = pygame.Surface(W_FB_SIZE).convert_alpha()


# ------------------------------------------------------------------------ #
# init
# ------------------------------------------------------------------------ #

DAMPING_FACTOR = 0.1
SIMULATION_SIZE = 100
DISTANCE_THRESHOLD = 100


UP = pygame.Vector2(0, 1)
INIT_SPEED_RANGE = (30, 150)

BOID_TRIANGLE = [
    pygame.Vector2(0, 10),
    pygame.Vector2(-6, -6),
    pygame.Vector2(6, -6),
]
BOID_LOGIC_CONSTANTS = {
    # "push_factor": 0.3,
    # "steer_factor": 0.4,
    "push_factor": 0,
    "steer_factor": 0,
    "cohesion_factor": 0.8,
}

# create the boids container
_boids_container = {}

# create default boids
for i in range(SIMULATION_SIZE):
    _boid = boid.Boid()
    _boid._position.xy = (
        random.randint(0, W_FB_SIZE[0]),
        random.randint(0, W_FB_SIZE[1]),
    )
    _boid._velocity.xy = (
        random.random() * 2 - 1,
        random.random() * 2 - 1,
    )
    _boid._velocity *= random.randint(INIT_SPEED_RANGE[0], INIT_SPEED_RANGE[1])
    _boid._acceleration.xy = (0, 0)

    # add to container
    _boids_container[_boid._id] = _boid


# ------------------------------------------------------------------------ #
# functions
# ------------------------------------------------------------------------ #


def boid_logic(boid: boid.Boid, boids):
    """

    This function only changes 1 things:
    - the acceleration

    That's it lol.

    it'll take data from all the neighboring boids + calculate the acceleration
    based on the rules of flocking behavior.

    1. Separation: steer to avoid crowding local flockmates
    2. Alignment: steer towards the average heading of local flockmates
    3. Cohesion: steer to move toward the average position of local flockmates
    """

    _nearby = []
    for _key in boids.keys():
        if _key != boid._id:
            other_boid = boids[_key]
            distance = boid._position.distance_to(other_boid._position)
            if distance < DISTANCE_THRESHOLD:
                _nearby.append(other_boid)

    if not _nearby:
        return

    # factors
    _steer_factor = boid._velocity.copy()
    _push_factor = pygame.Vector2(0, 0)
    _cohesion_factor = boid._position.copy()

    for _other_boid in _nearby:
        _displacement = boid._position - _other_boid._position
        _displacement_length = _displacement.length()

        # push factor - avoid others
        _push_factor += _displacement / (_displacement_length**2)
        # steer factor - follow others directions
        _steer_factor += _other_boid._velocity.normalize()
        # cohesion factor - average of neighbors
        _cohesion_factor += _other_boid._position / _displacement_length

    # step 1: calculate push factor
    if _push_factor.length() > 0:
        _push_factor /= len(_nearby)
        _push_factor = _push_factor.normalize()
        _push_factor = _push_factor * 10
        _push_factor = _push_factor - boid._velocity
        if _push_factor.length() > 10:
            _push_factor = _push_factor.normalize() * 10

    # step 2: calculate steer factor
    if _steer_factor.length() > 0:
        _steer_factor /= len(_nearby) + 1
        _steer_factor.normalize_ip()
        _steer_factor = _steer_factor - boid._velocity.normalize()

        if _steer_factor.length() > 10:
            _steer_factor = _steer_factor.normalize() * 10

    # step 3: calculate cohesion factor
    if _cohesion_factor.length() > 0:
        _cohesion_factor /= len(_nearby) + 1
        _cohesion_factor = _cohesion_factor - boid._position
        _cohesion_factor.normalize_ip()
        _cohesion_factor = _cohesion_factor * 10
        _cohesion_factor = _cohesion_factor - boid._velocity

        if _cohesion_factor.length() > 10:
            _cohesion_factor = _cohesion_factor.normalize() * 10

    print(_push_factor, _steer_factor, _cohesion_factor)

    # finalize acceleration
    boid._acceleration.xy = _push_factor + _steer_factor + _cohesion_factor
    if boid._acceleration.length() > 0:
        boid._acceleration = boid._acceleration.normalize() * 50


def _handle_boids(boids, surface, delta):
    # draw triangles surrounding the boids
    for _key in boids.keys():
        boid = boids[_key]
        color = boid._color
        position = boid._position
        velocity = boid._velocity

        # implement boid logic
        boid_logic(boid, boids)

        # keep boid velocity in a certain range
        if boid._velocity.length() < INIT_SPEED_RANGE[0]:
            boid._velocity = boid._velocity.normalize() * INIT_SPEED_RANGE[0]
        if boid._velocity.length() > INIT_SPEED_RANGE[1]:
            boid._velocity = boid._velocity.normalize() * INIT_SPEED_RANGE[1]

        # move boid
        boid._position += boid._velocity * delta
        boid._velocity += boid._acceleration * delta

        # check if out of bounds
        if boid._position.x < 0:
            boid._position.x = W_FB_SIZE[0]
        if boid._position.x > W_FB_SIZE[0]:
            boid._position.x = 0
        if boid._position.y < 0:
            boid._position.y = W_FB_SIZE[1]
        if boid._position.y > W_FB_SIZE[1]:
            boid._position.y = 0

        # calculate angle of rotation
        angle = UP.angle_to(velocity)

        # rotate triangle
        rotated_triangle = [point.rotate(angle) + position for point in BOID_TRIANGLE]

        # draw lines
        pygame.draw.lines(surface, color, True, rotated_triangle, width=3)
        pygame.draw.line(
            surface,
            (255, 0, 0),
            position,
            position + velocity.normalize() * 20,
            width=1,
        )


# ------------------------------------------------------------------------ #
# pygame sliders
# ------------------------------------------------------------------------ #

# ui_manager = pygame_gui.UIManager((W_SIZE[0], W_SIZE[1]), "theme.json")

# panel_rect = pygame.Rect((W_SIZE[0] - 200, 0), (200, 200))  # x, y, width, height
# control_panel = pygame_gui.elements.UIPanel(
#     relative_rect=panel_rect, manager=ui_manager, starting_layer_height=1
# )

# # separation
# label_separation = pygame_gui.elements.UILabel(
#     relative_rect=pygame.Rect((10, 10), (180, 20)),
#     text="Separation",
#     manager=ui_manager,
#     container=control_panel,
# )

# slider_separation = pygame_gui.elements.UIHorizontalSlider(
#     relative_rect=pygame.Rect((10, 35), (180, 20)),
#     start_value=BOID_LOGIC_CONSTANTS["push_factor"],
#     value_range=(0.0, 1.0),
#     manager=ui_manager,
#     container=control_panel,
# )

# # alignment
# label_alignment = pygame_gui.elements.UILabel(
#     relative_rect=pygame.Rect((10, 50), (180, 20)),
#     text="Alignment",
#     manager=ui_manager,
#     container=control_panel,
# )

# slider_alignment = pygame_gui.elements.UIHorizontalSlider(
#     relative_rect=pygame.Rect((10, 75), (180, 20)),
#     start_value=BOID_LOGIC_CONSTANTS["steer_factor"],
#     value_range=(0.0, 1.0),
#     manager=ui_manager,
#     container=control_panel,
# )

# # cohesion
# label_cohesion = pygame_gui.elements.UILabel(
#     relative_rect=pygame.Rect((10, 90), (180, 20)),
#     text="Cohesion",
#     manager=ui_manager,
#     container=control_panel,
# )
# slider_cohesion = pygame_gui.elements.UIHorizontalSlider(
#     relative_rect=pygame.Rect((10, 105), (180, 20)),
#     start_value=BOID_LOGIC_CONSTANTS["cohesion_factor"],
#     value_range=(0.0, 1.0),
#     manager=ui_manager,
#     container=control_panel,
# )

# ------------------------------------------------------------------------ #
# game loop
# ------------------------------------------------------------------------ #


W_RUNNING = True
while W_RUNNING:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            W_RUNNING = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                W_RUNNING = False

    #         # Pass events to the UI manager
    #     ui_manager.process_events(e)

    # # Update the UI manager
    # ui_manager.update(delta_time=W_DELTA)

    # # Retrieve slider values
    # BOID_LOGIC_CONSTANTS["push_factor"] = slider_separation.get_current_value()
    # BOID_LOGIC_CONSTANTS["steer_factor"] = slider_alignment.get_current_value()
    # BOID_LOGIC_CONSTANTS["cohesion_factor"] = slider_cohesion.get_current_value()

    # update game state
    W_FRAMEBUFFER.fill(W_BACKGROUND_COLOR)

    # handle boids
    _handle_boids(_boids_container, W_FRAMEBUFFER, W_DELTA)

    # render to window
    W_WINDOW.blit(pygame.transform.scale(W_FRAMEBUFFER, W_BUF_SIZE), W_BUF_POS)
    pygame.display.flip()

    W_DELTA = W_CLOCK.tick(W_FPS) / 1000


pygame.quit()
