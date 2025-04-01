import pygame

import engine.context as ctx
import engine.constants as consts

from engine.physics import interact
from engine.physics.ecs import c_AABB

import engine.ecs.c_sprite as c_sprite

# ------------------------------------------------------------------------ #
# resolve aabb aabb
# ------------------------------------------------------------------------ #


def _resolve_aabb_aabb(manifold: interact.CollisionManifold):
    # no resolution required
    return None


interact.InteractionField.cache_resolution_function(
    c_AABB.AABBColliderComponent, c_AABB.AABBColliderComponent, _resolve_aabb_aabb
)


# ------------------------------------------------------------------------ #
# resolve aabb sorabox2d
# ------------------------------------------------------------------------ #

from engine.physics.ecs import c_SoraBox2D


def _resolve_aabb_sorabox2d(manifold: interact.CollisionManifold):
    s_interact, d_interact = manifold._interact1, manifold._interact2
    s_entity, d_entity = s_interact._entity, d_interact._entity
    s_shape, d_shape = s_interact._shape, d_interact._shape

    # who is static?
    # print(manifold)

    s_rect = pygame.FRect(
        (0, 0),
        s_interact._shape._rect.size,
    )
    s_rect.center = s_entity._prev_position.copy()

    d_rect = pygame.FRect(
        (0, 0),
        d_interact._shape._rect.size,
    )
    d_rect.center = d_entity._prev_position.copy()

    # stage 1: basic SAT collision
    # stage 1.1: move in x-axis
    d_rect.x += d_interact._velocity.x * consts.DELTA_TIME

    # check for collision
    if s_rect.colliderect(d_rect):
        # resolve collision
        # reset velocity
        if d_interact._velocity.x > 0:
            d_rect.right = s_rect.left
        else:
            d_rect.left = s_rect.right
        d_interact._velocity.x *= -d_shape._collision_conserve_coef

    # stage 1.2: move in y-axis
    d_rect.y += d_interact._velocity.y * consts.DELTA_TIME

    # check for collision
    if s_rect.colliderect(d_rect):
        # resolve collision
        # reset velocity
        if d_interact._velocity.y > 0:
            d_rect.bottom = s_rect.top
        else:
            d_rect.top = s_rect.bottom
        d_interact._velocity.y *= -d_shape._collision_conserve_coef

    # stage 2: update entity position
    d_entity._position.xy = d_rect.center


interact.InteractionField.cache_resolution_function(
    c_AABB.AABBColliderComponent,
    c_SoraBox2D.SoraBox2DColliderComponent,
    _resolve_aabb_sorabox2d,
)

# ------------------------------------------------------------------------ #
# resolve sorabox2d sorabox2d
# ------------------------------------------------------------------------ #


def _resolve_sorabox2d_sorabox2d(manifold: interact.CollisionManifold):
    # no collision
    return None


interact.InteractionField.cache_resolution_function(
    c_SoraBox2D.SoraBox2DColliderComponent,
    c_SoraBox2D.SoraBox2DColliderComponent,
    _resolve_sorabox2d_sorabox2d,
)
