import pygame
import random
import math

from source import boid

# ------------------------------------------------------------------------ #
# setup
# ------------------------------------------------------------------------ #

# constants
W_RUNNING = False
W_SIZE = [1280, 720]
W_FB_SIZE = [1920, 1080]
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
SIMULATION_SIZE = 250
DISTANCE_THRESHOLD = W_FB_SIZE[0] / 7


UP = pygame.Vector2(0, 1)
INIT_SPEED_RANGE = (70, 150)

BOID_TRIANGLE = [
    pygame.Vector2(0, 10),
    pygame.Vector2(-6, -6),
    pygame.Vector2(6, -6),
]
BOID_LOGIC_CONSTANTS = {
    "push_factor": 0.4,
    "steer_factor": 0.7,
    "cohesion_factor": 0.6,
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
        _displacement = _other_boid._position - boid._position
        _displacement_length = _displacement.length()

        # push factor - avoid others
        if _displacement_length > 0:
            _push_factor += _displacement / (_displacement_length**2)
        # steer factor - follow others directions
        _steer_factor += _other_boid._velocity.normalize() * (
            DISTANCE_THRESHOLD - _displacement_length
        )
        # cohesion factor - average of neighbors
        _cohesion_factor += _other_boid._position

    # step 1: calculate push factor
    if _push_factor.length() > 0:
        _push_factor = _push_factor.normalize() * -1

    # step 2: calculate steer factor
    if _steer_factor.length() > 0:
        _steer_factor.normalize_ip()

    # step 3: calculate cohesion factor
    if _cohesion_factor.length() > 0:
        _cohesion_factor /= len(_nearby) + 1
        _cohesion_factor = _cohesion_factor - boid._position

    # finalize acceleration
    boid._push = _push_factor * len(_nearby) * BOID_LOGIC_CONSTANTS["push_factor"]
    boid._steer = _steer_factor * len(_nearby) * BOID_LOGIC_CONSTANTS["steer_factor"]
    boid._cohesion = _cohesion_factor * BOID_LOGIC_CONSTANTS["cohesion_factor"]
    boid._cohesion_point = _cohesion_factor
    boid._acceleration.xy = boid._push + boid._steer + boid._cohesion


def _handle_boids(boids, surface, delta):
    main_boid = boids[list(boids.keys())[0]]
    print(
        f"{main_boid._id} | "
        f"{main_boid._push.x:>7.2f}, {main_boid._push.y:>7.2f} | "
        f"{main_boid._steer.x:>7.2f}, {main_boid._steer.y:>7.2f} | "
        f"{main_boid._cohesion.x:>7.2f}, {main_boid._cohesion.y:>7.2f}"
    )
    # draw triangles surrounding the boids
    for _key in boids.keys():
        boid = boids[_key]
        color = boid._color if main_boid._id == boid._id else (255, 0, 255)
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
        if not pygame.key.get_pressed()[pygame.K_SPACE]:
            boid._position += boid._velocity * delta
            boid._velocity += boid._acceleration * delta
            boid._velocity.rotate_ip(random.randint(-10, 10))

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

        # draw push, steer, and cohesion vectors
        pygame.draw.line(
            surface,
            (255, 255, 0),
            position,
            # position + velocity.normalize() * 20,
            (
                position + boid._push.normalize() * 20
                if boid._push.length() > 0
                else position
            ),
            width=1,
        )
        pygame.draw.line(
            surface,
            (0, 255, 0),
            position,
            # position + velocity.normalize() * 20,
            (
                position + boid._steer.normalize() * 20
                if boid._steer.length() > 0
                else position
            ),
            width=1,
        )
        pygame.draw.line(
            surface,
            (255, 0, 0),
            position,
            # position + velocity.normalize() * 20,
            (
                position + boid._cohesion.normalize() * 20
                if boid._cohesion.length() > 0
                else position
            ),
            width=1,
        )

        # draw a circle
        if main_boid._id == boid._id:
            pygame.draw.circle(
                surface, (0, 255, 0), position, DISTANCE_THRESHOLD, width=1
            )
            # draw weighted average flock position
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                position + boid._cohesion_point,
                5,
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
