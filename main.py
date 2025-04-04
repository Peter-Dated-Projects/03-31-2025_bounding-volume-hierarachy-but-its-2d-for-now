import time
import pygame
import random
import math

from source import boid
from source import ui
from source import bvh

# ------------------------------------------------------------------------ #
# setup
# ------------------------------------------------------------------------ #

# constants
W_RUNNING = False
W_SIZE = [1280, 720]
# W_FB_SIZE = [1920, 1080]
W_FB_SIZE = [1920, 1080]
W_FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SRCALPHA
W_BIT_DEPTH = 32
W_BACKGROUND_COLOR = (0, 17, 41, 255)
W_CLOCK = pygame.time.Clock()

W_BUF_SIZE = (W_SIZE[0] * 1.03, W_SIZE[1] * 1.03)
W_BUF_POS = (-(W_BUF_SIZE[0] - W_SIZE[0]) // 2, -(W_BUF_SIZE[1] - W_SIZE[1]) // 2)

W_GLOBAL_START = time.time()
W_START = time.time()
W_END = time.time()
W_DELTA = 1 / 60
W_FPS = 60

# surfaces
W_WINDOW = pygame.display.set_mode(W_SIZE, W_FLAGS, W_BIT_DEPTH)
W_FRAMEBUFFER = pygame.Surface(W_FB_SIZE).convert_alpha()


# ------------------------------------------------------------------------ #
# init
# ------------------------------------------------------------------------ #

DAMPING_FACTOR = 0.1
SIMULATION_SIZE = 700


UP = pygame.Vector2(0, 1)
INIT_SPEED_RANGE = [70, 150]

BOID_TRIANGLE = [
    pygame.Vector2(0, 10),
    pygame.Vector2(-6, -6),
    pygame.Vector2(6, -6),
]
BOID_LOGIC_CONSTANTS = {
    "push_factor": 48,
    "steer_factor": 4.85,
    "cohesion_factor": 149,
    "enable_push": 1,
    "enable_steer": 1,
    "enable_cohesion": 1,
    "enable_random_movement": 1,
    "random_angle": 2,
    "distance_threshold": 130,
    # "distance_threshold": 30,
    "only_bvh_leaf": True,
    # for debugging
    "enable_vectors": False,
    "use_bvh": True,
}

# create the boids container
_boids_container = {}
_bounding_volume_hierarchy = bvh.BVHContainer2D(
    world_area=pygame.FRect(0, 0, W_FB_SIZE[0], W_FB_SIZE[1]),
    objects=[],
    max_depth=4,
)


def _create_world():
    global _boids_container

    _boids_container.clear()

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
    _bounding_volume_hierarchy.update(list(_boids_container.values()))


# ------------------------------------------------------------------------ #
# functions
# ------------------------------------------------------------------------ #


def iterate_nearby_boids(bvh, boids, boid):
    """
    Iterate through the nearby boids in the BVH.
    """
    _nodes = bvh.get_colliding_nodes(
        pygame.FRect(
            boid._position.x - BOID_LOGIC_CONSTANTS["distance_threshold"],
            boid._position.y - BOID_LOGIC_CONSTANTS["distance_threshold"],
            BOID_LOGIC_CONSTANTS["distance_threshold"] * 2,
            BOID_LOGIC_CONSTANTS["distance_threshold"] * 2,
        )
    )

    for node in _nodes:
        for _other_boid in node._objects:
            # check if the boid is not the same as the other boid
            if boid._id != _other_boid._id:
                yield _other_boid


def iterate_nearby_boids_no_bvh(bvh, boids, boid):
    """
    Iterate through the nearby boids in the BVH.
    """
    for _other_boid in boids.values():
        # check if the boid is not the same as the other boid
        if boid._id != _other_boid._id:
            _displacement = _other_boid._position - boid._position
            if _displacement.length() < BOID_LOGIC_CONSTANTS["distance_threshold"]:
                yield _other_boid


def boid_logic(boid: boid.Boid, boids: dict, bvh: bvh.BVHContainer2D):
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

    # factors
    _steer_factor = boid._velocity.copy()
    _push_factor = pygame.Vector2(0, 0)
    _cohesion_factor = pygame.Vector2(0, 0)
    _nearby_boids = 0

    _iter_func = (
        iterate_nearby_boids
        if BOID_LOGIC_CONSTANTS["use_bvh"] == 1
        else iterate_nearby_boids_no_bvh
    )

    for _other_boid in _iter_func(bvh, boids, boid):
        _displacement = _other_boid._position - boid._position
        _displacement_length = _displacement.length()

        # push factor - avoid others
        if _displacement_length > 0:
            _push_factor += _displacement / _displacement_length**2 * 10
        # steer factor - follow others directions
        _steer_factor += _other_boid._velocity
        # cohesion factor - average of neighbors
        _cohesion_factor += _other_boid._position

        _nearby_boids += 1
    if _nearby_boids == 0:
        return

    # step 1: calculate push factor
    if _push_factor.length() > 0:
        _push_factor *= -1

    # step 2: calculate steer factor
    if _steer_factor.length() > 0:
        _steer_factor /= _nearby_boids
        _steer_factor = _steer_factor.normalize() * _nearby_boids

    # step 3: calculate cohesion factor
    boid._cohesion_point = _cohesion_factor.copy()
    if _cohesion_factor.length() > 0:
        _cohesion_factor /= _nearby_boids
        _cohesion_factor = _cohesion_factor - boid._position

        _cohesion_factor.normalize_ip()

    # finalize acceleration
    boid._push = (
        _push_factor
        * BOID_LOGIC_CONSTANTS["push_factor"]
        * BOID_LOGIC_CONSTANTS["enable_push"]
    )
    boid._steer = (
        _steer_factor
        * BOID_LOGIC_CONSTANTS["steer_factor"]
        * BOID_LOGIC_CONSTANTS["enable_steer"]
    )
    boid._cohesion = (
        _cohesion_factor
        * BOID_LOGIC_CONSTANTS["cohesion_factor"]
        * BOID_LOGIC_CONSTANTS["enable_cohesion"]
    )
    boid._acceleration.xy = boid._push + boid._steer + boid._cohesion


def _handle_boids(boids, bvh, surface, delta):
    main_boid = boids[list(boids.keys())[0]]
    # print(
    #     f"{main_boid._id} | "
    #     f"{main_boid._push.x:>7.2f}, {main_boid._push.y:>7.2f} | "
    #     f"{main_boid._steer.x:>7.2f}, {main_boid._steer.y:>7.2f} | "
    #     f"{main_boid._cohesion.x:>7.2f}, {main_boid._cohesion.y:>7.2f}"
    # )

    # print(BOID_LOGIC_CONSTANTS)
    # draw triangles surrounding the boids
    for _key in boids.keys():
        boid = boids[_key]
        color = boid._color if main_boid._id == boid._id else (255, 0, 255)
        position = boid._position
        velocity = boid._velocity

        # implement boid logic
        boid_logic(boid, boids, bvh)

        # keep boid velocity in a certain range
        if boid._velocity.length() < INIT_SPEED_RANGE[0]:
            boid._velocity = boid._velocity.normalize() * INIT_SPEED_RANGE[0]
        if boid._velocity.length() > INIT_SPEED_RANGE[1] + INIT_SPEED_RANGE[0]:
            boid._velocity = boid._velocity.normalize() * (
                INIT_SPEED_RANGE[1] + INIT_SPEED_RANGE[0]
            )

        # move boid
        boid._position += boid._velocity * delta
        boid._velocity += boid._acceleration * delta
        if BOID_LOGIC_CONSTANTS["enable_random_movement"] == 1:
            boid._velocity.rotate_ip(
                random.randint(
                    -BOID_LOGIC_CONSTANTS["random_angle"],
                    BOID_LOGIC_CONSTANTS["random_angle"],
                )
            )

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

        if not BOID_LOGIC_CONSTANTS["enable_vectors"]:
            continue

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
                surface,
                (0, 255, 0),
                position,
                BOID_LOGIC_CONSTANTS["distance_threshold"],
                width=1,
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

if True:
    ui_container = ui.UI(pygame.FRect(0, 0, 200, 400))

    # activate push or not
    def update_push_factor():
        if BOID_LOGIC_CONSTANTS["enable_push"] == 1:
            BOID_LOGIC_CONSTANTS["enable_push"] = 0
        else:
            BOID_LOGIC_CONSTANTS["enable_push"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 0, 200, 30),
            text="Enable Push Factor",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(200, 0, 25, 25),
            onclick=update_push_factor,
            default_value=BOID_LOGIC_CONSTANTS["enable_push"],
        )
    )

    # activate steer or not
    def update_steer_factor():
        if BOID_LOGIC_CONSTANTS["enable_steer"] == 1:
            BOID_LOGIC_CONSTANTS["enable_steer"] = 0
        else:
            BOID_LOGIC_CONSTANTS["enable_steer"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 30, 200, 30),
            text="Enable Steer Factor",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(200, 30, 25, 25),
            onclick=update_steer_factor,
            default_value=BOID_LOGIC_CONSTANTS["enable_steer"],
        )
    )

    # activate cohesion or not
    def update_cohesion_factor():
        if BOID_LOGIC_CONSTANTS["enable_cohesion"] == 1:
            BOID_LOGIC_CONSTANTS["enable_cohesion"] = 0
        else:
            BOID_LOGIC_CONSTANTS["enable_cohesion"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 60, 200, 30),
            text="Enable Cohesion Factor",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(250, 60, 25, 25),
            onclick=update_cohesion_factor,
            default_value=BOID_LOGIC_CONSTANTS["enable_cohesion"],
        )
    )

    # random movement or not
    def update_random_movement():
        if BOID_LOGIC_CONSTANTS["enable_random_movement"] == 1:
            BOID_LOGIC_CONSTANTS["enable_random_movement"] = 0
        else:
            BOID_LOGIC_CONSTANTS["enable_random_movement"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 90, 200, 30),
            text="Enable Random Movement",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(250, 90, 25, 25),
            onclick=update_random_movement,
            default_value=BOID_LOGIC_CONSTANTS["enable_random_movement"],
        )
    )

    # add sliders for push, steer, and cohesion factors
    def update_push_factor_ui(value):
        # update the push factor in the boid logic constants
        BOID_LOGIC_CONSTANTS["push_factor"] = value

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 120, 200, 20),
            text="Push Factor",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 150, 200, 20),
            min_value=0,
            max_value=100,
            default_value=BOID_LOGIC_CONSTANTS["push_factor"],
            update_func=update_push_factor_ui,
        )
    )

    # add slider for steer factor
    def update_steer_factor_ui(value):
        # update the steer factor in the boid logic constants
        BOID_LOGIC_CONSTANTS["steer_factor"] = value

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 180, 200, 20),
            text="Steer Factor",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 210, 200, 20),
            min_value=0,
            max_value=10,
            default_value=BOID_LOGIC_CONSTANTS["steer_factor"],
            update_func=update_steer_factor_ui,
        )
    )

    # add slider for cohesion factor
    def update_cohesion_factor_ui(value):
        # update the cohesion factor in the boid logic constants
        BOID_LOGIC_CONSTANTS["cohesion_factor"] = value

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 240, 200, 20),
            text="Cohesion Factor",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 270, 200, 20),
            min_value=0,
            max_value=200,
            default_value=BOID_LOGIC_CONSTANTS["cohesion_factor"],
            update_func=update_cohesion_factor_ui,
        )
    )

    # add slider for min speed
    def update_min_speed_ui(value):
        # update the min speed in the boid logic constants
        INIT_SPEED_RANGE[0] = value

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 300, 200, 20),
            text="Min Speed",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 330, 200, 20),
            min_value=10,
            max_value=500,
            default_value=INIT_SPEED_RANGE[0],
            update_func=update_min_speed_ui,
        )
    )

    # add slider for detection radius
    def update_detection_radius_ui(value):
        # update the detection radius in the boid logic constants
        BOID_LOGIC_CONSTANTS["distance_threshold"] = value

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 360, 200, 20),
            text="Detection Radius",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 390, 200, 20),
            min_value=0,
            max_value=500,
            default_value=BOID_LOGIC_CONSTANTS["distance_threshold"],
            update_func=update_detection_radius_ui,
        )
    )

    # add a toggle for show boid vectors
    def update_show_vectors():
        if BOID_LOGIC_CONSTANTS["enable_vectors"] == 1:
            BOID_LOGIC_CONSTANTS["enable_vectors"] = 0
        else:
            BOID_LOGIC_CONSTANTS["enable_vectors"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 420, 200, 20),
            text="Show Vectors",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(200, 420, 25, 25),
            onclick=update_show_vectors,
            default_value=BOID_LOGIC_CONSTANTS["enable_vectors"],
        )
    )

    # add a slider for random angle
    def update_random_angle_ui(value):
        # update the random angle in the boid logic constants
        BOID_LOGIC_CONSTANTS["random_angle"] = int(value)

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 450, 200, 20),
            text="Random Angle",
        )
    )
    ui_container.add_element(
        ui.UISlider(
            pygame.FRect(0, 480, 200, 20),
            min_value=0,
            max_value=20,
            default_value=BOID_LOGIC_CONSTANTS["random_angle"],
            update_func=update_random_angle_ui,
        )
    )

    # add a button for only bvh leaf
    def update_only_bvh_leaf():
        if BOID_LOGIC_CONSTANTS["only_bvh_leaf"] == 1:
            BOID_LOGIC_CONSTANTS["only_bvh_leaf"] = 0
        else:
            BOID_LOGIC_CONSTANTS["only_bvh_leaf"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 510, 200, 20),
            text="Only BVH Leaf",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(200, 510, 25, 25),
            onclick=update_only_bvh_leaf,
            default_value=BOID_LOGIC_CONSTANTS["only_bvh_leaf"],
        )
    )

    # use bvh
    def update_use_bvh():
        if BOID_LOGIC_CONSTANTS["use_bvh"] == 1:
            BOID_LOGIC_CONSTANTS["use_bvh"] = 0
        else:
            BOID_LOGIC_CONSTANTS["use_bvh"] = 1

    ui_container.add_element(
        ui.UILabel(
            pygame.FRect(0, 540, 200, 20),
            text="Use BVH",
        )
    )
    ui_container.add_element(
        ui.UIButton(
            pygame.FRect(200, 540, 25, 25),
            onclick=update_use_bvh,
            default_value=BOID_LOGIC_CONSTANTS["use_bvh"],
        )
    )

# ------------------------------------------------------------------------ #
# bvh
# ------------------------------------------------------------------------ #


def _handle_bvh(boids, surface, delta):
    # update the bvh
    _bounding_volume_hierarchy.update(list(boids.values()))

    # draw the bvh
    _bounding_volume_hierarchy.draw(
        surface,
        only_leaf=BOID_LOGIC_CONSTANTS["only_bvh_leaf"],
        draw_vectors=BOID_LOGIC_CONSTANTS["enable_vectors"],
    )


# ------------------------------------------------------------------------ #
# game loop
# ------------------------------------------------------------------------ #

_create_world()
_handle_boids(_boids_container, _bounding_volume_hierarchy, W_FRAMEBUFFER, W_DELTA)
_handle_bvh(_boids_container, W_FRAMEBUFFER, W_DELTA)

W_GLOBAL_START = time.time()

W_RUNNING = True

_delta_total = 0
_frame_total = 0

while W_RUNNING:

    W_START = time.time()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            W_RUNNING = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                W_RUNNING = False
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_SPACE:
                # show ui
                ui_container._visible = not ui_container._visible
            elif e.key == pygame.K_r:
                # reset boids
                _create_world()
        if e.type == pygame.VIDEORESIZE:
            W_SIZE = e.w, e.h
            W_WINDOW = pygame.display.set_mode(W_SIZE, W_FLAGS, W_BIT_DEPTH)
            W_BUF_SIZE = (W_SIZE[0] * 1.03, W_SIZE[1] * 1.03)
            W_BUF_POS = (
                -(W_BUF_SIZE[0] - W_SIZE[0]) // 2,
                -(W_BUF_SIZE[1] - W_SIZE[1]) // 2,
            )

    # update game state
    W_FRAMEBUFFER.fill(W_BACKGROUND_COLOR)

    if not pygame.key.get_pressed()[pygame.K_BACKSPACE]:
        # handle objects + rendering
        _handle_boids(
            _boids_container, _bounding_volume_hierarchy, W_FRAMEBUFFER, W_DELTA
        )
        _handle_bvh(_boids_container, W_FRAMEBUFFER, W_DELTA)

        # render to window
        W_WINDOW.blit(pygame.transform.scale(W_FRAMEBUFFER, W_BUF_SIZE), W_BUF_POS)

    # draw ui
    ui_container.draw(W_WINDOW)

    pygame.display.flip()
    W_END = time.time()
    W_DELTA = W_END - W_START

    _delta_total += W_DELTA
    _frame_total += 1

    W_DELTA = W_CLOCK.tick(W_FPS) / 1000

    # auto stop after 10 seconds
    # if time.time() - W_GLOBAL_START > 10:
    #     W_RUNNING = False

    print(time.time() - W_GLOBAL_START)


print(_delta_total / _frame_total * 1000)
pygame.quit()
