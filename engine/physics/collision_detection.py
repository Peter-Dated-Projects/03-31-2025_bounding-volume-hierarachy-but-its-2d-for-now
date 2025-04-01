import pygame

import engine.context as ctx
import engine.constants as consts

from engine.physics import interact
from engine.physics.ecs import c_AABB

# ------------------------------------------------------------------------ #
# detect aabb aabb
# ------------------------------------------------------------------------ #


def _detect_aabb_aabb(
    interact1: interact.InteractionFieldComponent,
    interact2: interact.InteractionFieldComponent,
):
    # check if the two colliders are intersecting
    shape1 = interact1._shape
    shape2 = interact2._shape

    shape1._rect.center = interact1._entity._position
    shape2._rect.center = interact2._entity._position

    if not shape1._rect.colliderect(shape2._rect):
        return None

    # return the manifold + calculate everything with custom information
    ab1 = shape1.get_abspoints()
    ab2 = shape2.get_abspoints()

    # print(f"{consts.RUN_TIME:.5f} | AB1: {ab1}, ENTITY_POS: {interact1._entity._position}")
    # print(f"{consts.RUN_TIME:.5f} | AB2: {ab2}, ENTITY_POS: {interact2._entity._position}")

    result = interact.CollisionManifold(
        interact1,
        interact2,
        consts.CTX_WORLD,
        extra={
            "penetration": pygame.Vector2(
                interact.single_axis_test(
                    ab1,
                    ab2,
                    consts.Constants.RIGHT,
                )
                / 2,
                interact.single_axis_test(
                    ab1,
                    ab2,
                    consts.Constants.UP,
                )
                / 2,
            )
        },
    )

    return result


interact.InteractionField.cache_detection_function(
    c_AABB.AABBColliderComponent, c_AABB.AABBColliderComponent, _detect_aabb_aabb
)

# ------------------------------------------------------------------------ #
# detect box2d aabb
# ------------------------------------------------------------------------ #

from engine.physics.ecs import c_SoraBox2D


def _detect_aabb_sorabox2d(
    interact1: interact.InteractionFieldComponent,
    interact2: interact.InteractionFieldComponent,
):
    # check if the two colliders are intersecting
    shape1 = interact1._shape
    shape2 = interact2._shape

    shape1._rect.center = interact1._entity._position
    shape2._rect.center = interact2._entity._position

    if not shape1._rect.colliderect(shape2._rect):
        return None

    # return the manifold + calculate everything
    ab1 = shape1.get_abspoints()
    ab2 = shape2.get_abspoints()

    # print(f"{consts.RUN_TIME:.5f} | AB1: {ab1}, ENTITY_POS: {interact1._entity._position}")
    # print(f"{consts.RUN_TIME:.5f} | AB2: {ab2}, ENTITY_POS: {interact2._entity._position}")

    # we only care if they hit or not
    result = interact.CollisionManifold(interact1, interact2, consts.CTX_WORLD)

    return result


interact.InteractionField.cache_detection_function(
    c_AABB.AABBColliderComponent,
    c_SoraBox2D.SoraBox2DColliderComponent,
    _detect_aabb_sorabox2d,
)

# ------------------------------------------------------------------------ #
# detect sorabox2d sorabox2d
# ------------------------------------------------------------------------ #


def _detect_sorabox2d_sorabox2d(
    interact1: interact.InteractionFieldComponent,
    interact2: interact.InteractionFieldComponent,
):
    # check if the two colliders are intersecting
    shape1 = interact1._shape
    shape2 = interact2._shape

    shape1._rect.center = interact1._entity._position
    shape2._rect.center = interact2._entity._position

    if not shape1._rect.colliderect(shape2._rect):
        return None

    # return the manifold + calculate everything
    ab1 = shape1.get_abspoints()
    ab2 = shape2.get_abspoints()

    # we only care if they hit or not
    result = interact.CollisionManifold(interact1, interact2, consts.CTX_WORLD)

    return result


interact.InteractionField.cache_detection_function(
    c_SoraBox2D.SoraBox2DColliderComponent,
    c_SoraBox2D.SoraBox2DColliderComponent,
    _detect_sorabox2d_sorabox2d,
)
