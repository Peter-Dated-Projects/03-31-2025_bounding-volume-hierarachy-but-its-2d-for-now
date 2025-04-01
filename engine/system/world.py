import pygame

import Box2D
from Box2D import b2

import engine.context as ctx
import engine.constants as consts

from engine.ecs import c_task

from engine.graphics import camera

from engine.physics import entity
from engine.physics import interact

# ======================================================================== #
# World
# ======================================================================== #


class World2D(entity.Entity):

    def __init__(
        self,
        name: str,
        gravity: tuple = consts.DEFAULT_PHYSICS_GRAVITY.xy,
        _physics_pos_steps: int = consts.DEFAULT_PHYSICS_POS_STEPS,
        _physics_vel_steps: int = consts.DEFAULT_PHYSICS_VEL_STEPS,
    ):
        super().__init__()
        self._name = name

        # management information
        self._layers = {}
        self._layers_order = []
        self._delta_layers = []
        self._physics_world = b2.world(gravity=gravity, doSleep=True)

        # rendering information
        self._render_chunk_cache = set()
        self._camera = camera.Camera2D(render_distance=4)
        self._physics_pos_steps = _physics_pos_steps
        self._physics_vel_steps = _physics_vel_steps

        # entity management - entities are just "container" objects
        self._entities = {}
        self._delta_entities = []

        # gamestate + interaction field parents
        self._interaction_field = interact.InteractionField(self)
        self._gamestate = None

    def __post_init__(self):
        # default task for the aspect handler
        self._entity_chunk_change_task = c_task.TaskComponent(
            f"_{consts.ENGINE_NAME}_entity_chunk_change_task",
            self._entity_chunk_change_task,
        )
        consts.CTX_ECS_HANDLER.add_component(self._entity_chunk_change_task, self)

    def __on_clean__(self):
        pass

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def update(self):

        # TODO - check if camera moved chunks
        self._render_chunk_cache = set(self._camera.generate_visible_chunks())

        # update all layers
        for layer_index in self._layers_order:
            self._layers[layer_index].update()

        # physics
        self._interaction_field.update()
        self._physics_world.Step(
            consts.DELTA_TIME, self._physics_vel_steps, self._physics_pos_steps
        )
        self._physics_world.ClearForces()

        # ------------------------------------------------ #
        # finish up by updating layers
        for layer in self._delta_layers:
            self._layers.pop(layer)
        self._delta_layers.clear()

        # finish up by updating entities
        for entity in self._delta_entities:
            self._entities.pop(entity._entity_id)
        self._delta_entities.clear()

    def _entity_chunk_change_task(self):
        for entity in self._entities.values():

            # calculate new chunk
            entity._chunk_pos = (
                int(entity._position.x // consts.DEFAULT_CHUNK_PIXEL_WIDTH),
                int(entity._position.y // consts.DEFAULT_CHUNK_PIXEL_HEIGHT),
            )

            # check if entity moved chunks
            if entity._chunk_pos != entity._prev_chunk_pos:
                # remove entity from old chunk
                self.get_chunk(
                    entity._prev_chunk_pos, entity._prev_zlayer
                ).remove_not_clean(entity)
                # add entity to new chunk
                self.get_chunk(entity._chunk_pos, entity._zlayer).add_entity(entity)
                # update previous chunk position
                entity._prev_chunk_pos = entity._chunk_pos
                entity._prev_zlayer = entity._zlayer

                print(f"{consts.RUN_TIME:.5f} | ENTITY MOVED CHUNKS", entity)

    # ------------------------------------------------------------------------ #
    # layer logic
    # ------------------------------------------------------------------------ #

    def add_layer(self, layer: "Layer"):
        self._layers[layer._zlevel] = layer
        self._layers_order.append(layer._zlevel)
        layer._world = self
        layer.__post_init__()
        # sort layers
        self._layers_order.sort()

    def remove_layer(self, zlevel: int):
        self._delta_layers.append(zlevel)

    def get_layer(self, zlevel: int):
        if zlevel not in self._layers:
            self.add_layer(Layer(zlevel))
        return self._layers[zlevel]

    # ------------------------------------------------------------------------ #
    # chunk logic
    # ------------------------------------------------------------------------ #

    def add_chunk(self, chunk: "Chunk", zlayer: int):
        self.get_layer(zlayer).add_chunk(chunk)

    def remove_chunk(self, chunk: "Chunk", zlayer: int):
        self.get_layer(zlayer).remove_chunk(chunk)

    def get_chunk(self, chunk_position: tuple, zlayer: int):
        return self.get_layer(zlayer).get_chunk(chunk_position)

    # ------------------------------------------------------------------------ #
    # entity logic
    # ------------------------------------------------------------------------ #

    def add_entity(self, entity: "Entity"):
        self._entities[hash(entity)] = entity
        entity._world = self
        entity._layer = self.get_layer(entity._zlayer)
        entity.__post_init__()

        # create chunk
        self.get_chunk(entity._chunk_pos, entity._zlayer).add_entity(entity)
        return entity

    def remove_entity(self, entity: "Entity"):
        self._delta_entities.append(entity)

    def get_entity(self, entity_id: int):
        return self._entities.get(entity_id)

    # ------------------------------------------------------------------------ #
    # component logic
    # ------------------------------------------------------------------------ #

    def get_components(self, component_class: type):
        return self._gamestate._ecs.get_components(component_class)

    def get_components_by_type(self, component_class: type):
        return self._gamestate._ecs.get_components_by_type(component_class)

    def get_component(self, component_class: type, uuid: int):
        return self._gamestate._ecs.get_component(component_class, uuid)


# ======================================================================== #
# Layer
# ======================================================================== #


class Layer:
    def __init__(
        self,
        zlevel: int = 0,
        buffer: bool = False,
        buffer_size: tuple = None,
    ):
        self._zlevel = zlevel
        self._chunks = {}
        self._delta_chunks = []
        self._buffer = buffer

        # buffer information -- toggleable
        self._framebuffer = (
            None if not buffer else pygame.Surface(consts.W_FRAMEBUFFER.get_size())
        )
        self._buffer_size = buffer_size

        # management information
        self._world = None

    def __post_init__(self):
        # register the death signal for an entity
        consts.CTX_SIGNAL_HANDLER.register_signal(
            f"SORA_ENTITY_DEATH-{self._zlevel}", [entity.Entity]
        )

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def update(self):
        # update all chunks inside of this layer
        # TODO - add valid chunk filtering
        #       - something like: self._world.get_visible_chunks(self)
        for chunk in self._chunks.values():
            chunk.update()

        # finish up by updating chunks
        for chunk in self._delta_chunks:
            self.add_chunk(chunk)
        self._delta_chunks.clear()

    # ------------------------------------------------------------------------ #
    # chunk logic
    # ------------------------------------------------------------------------ #

    def add_chunk(self, chunk: "Chunk"):
        self._chunks[chunk._chunk_id] = chunk
        chunk._layer = self
        chunk.__post_init__()

    def remove_chunk(self, chunk: "Chunk"):
        self._delta_chunks.append(chunk)

    def get_chunk(self, chunk_position: tuple):
        if not Chunk.get_id(chunk_position) in self._chunks:
            self.add_chunk(Chunk(chunk_position))
        return self._chunks[Chunk.get_id(chunk_position)]


# ======================================================================== #
# Chunk
# ======================================================================== #


class Chunk:

    @staticmethod
    def get_id(chunk_position: tuple):
        return f"{int(chunk_position[0])}||{int(chunk_position[1])}"

    # ------------------------------------------------------------------------ #
    # init
    # ------------------------------------------------------------------------ #

    def __init__(self, chunk_position: tuple):
        self._chunk_position = chunk_position
        self._chunk_size = (
            consts.DEFAULT_CHUNK_PIXEL_WIDTH,
            consts.DEFAULT_CHUNK_PIXEL_HEIGHT,
        )

        # chunk information
        self._chunk_id = Chunk.get_id(self._chunk_position)

        # management information
        self._layer = None

        # entity information
        self._entities = {}

    def __post_init__(self):
        # register the death signal for an entity
        self._death_signal = consts.CTX_SIGNAL_HANDLER.register_receiver(
            f"SORA_ENTITY_DEATH-{self._layer._zlevel}", self._entity_death_logic
        )

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def update(self):
        # update all entities inside of this chunk
        for entity in self._entities.values():
            entity.update()
            entity.handle_components()
        if consts.DEBUG_MODE:
            for entity in self._entities.values():
                entity.debug()

    # ------------------------------------------------------------------------ #
    # entity logic
    # ------------------------------------------------------------------------ #

    def _entity_death_logic(self, entity: "Entity"):
        print(
            f"{consts.RUN_TIME:.5f} | ENTITY ZLAYER",
            entity._zlayer,
            self._layer._zlevel,
        )
        if (
            entity._zlayer != self._layer._zlevel
            or entity._zlayer != entity._prev_zlayer
        ):
            return
        self.remove_entity(entity)

    def add_entity(self, entity: "Entity"):
        print(
            f"{consts.RUN_TIME:.5f} | ADDING", entity, entity._entity_id, entity._zlayer
        )
        self._entities[entity._entity_id] = entity

    def remove_entity(self, entity: "Entity"):
        print(f"{consts.RUN_TIME:.5f} | REMOVING", entity._entity_id)
        self._entities.pop(entity._entity_id)
        entity.clean()

    def remove_not_clean(self, entity: "Entity"):
        self._entities.pop(entity._entity_id)
