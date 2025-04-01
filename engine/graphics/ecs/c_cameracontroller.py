import glm

from engine.system import ecs

from engine.graphpics import camera

# ============================================================================= #
# Camera Controller
# ============================================================================= #

_2D_CAMERA = 0
_3D_CAMERA = 1


class CameraController3D(ecs.Component):
    def __init__(self):
        super().__init__()

        self._camera = None

    def __post_init__(self):
        self._camera = self._entity

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def change_position(self, direction: glm.vec3):
        self._camera._position += direction

    def change_rotation(self, rotation: glm.vec3):
        self._camera.up = rotation

    def change_perspective(self, fov: float, near: float = 0, far: float = 0):
        self._camera.fov += fov
        self._camera.near += near
        self._camera.far += far

    def change_forward(self, forward: glm.vec3):
        self._camera.forward += forward

    # ------------------------------------------------------------------------ #
    # setters
    # ------------------------------------------------------------------------ #

    # position
    def set_position(self, position: glm.vec3):
        self._camera.position = position

    # rotation
    def set_rotation(self, rotation: glm.vec3):
        self._camera.rotation = rotation

    def set_x_rotation(self, rotation: float):
        self._camera.rotation.x = rotation

    def set_y_rotation(self, rotation: float):
        self._camera.rotation.y = rotation

    def set_z_rotation(self, rotation: float):
        self._camera.rotation.z = rotation

    # projection setters
    def set_perspective(self, fov: float, near: float = 0, far: float = 0):
        self._camera.fov = fov
        self._camera.near = near
        self._camera.far = far
        self._camera.calculate_projection()

    def set_fov(self, fov: float):
        self._camera.fov = fov
        self._camera.calculate_projection()

    def set_near(self, near: float):
        self._camera.near = near
        self._camera.calculate_projection()

    def set_far(self, far: float):
        self._camera.far = far
        self._camera.calculate_projection()

    def set_width(self, width: int):
        self._camera.width = width
        self._camera.calculate_projection()

    def set_height(self, height: int):
        self._camera.height = height
        self._camera.calculate_projection()

    # targets + lookat
    def set_target(self, target: glm.vec3):
        self._camera.target = target

    def set_forward(self, forward: glm.vec3):
        self._camera.forward = forward
