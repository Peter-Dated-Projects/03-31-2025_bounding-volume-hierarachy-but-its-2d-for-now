import pygame
import moderngl as mgl

import engine.context as ctx
import engine.constants as consts

# ============================================================================= #
# Texture
# ============================================================================= #


class Texture:
    # some static version of textures
    CACHE = {}
    NONE_FILE_CACHE = {}
    TEXTURE_COUNT = 0

    @classmethod
    def generate_texture_uuid(cls):
        cls.TEXTURE_COUNT += 1
        return cls.TEXTURE_COUNT

    @classmethod
    def get_texture(cls, path: str, xflip: bool = False, yflip: bool = False):
        if path in cls.CACHE:
            return cls.CACHE[path]

        # create texture
        texture = cls(path=path, xflip=xflip, yflip=yflip)
        cls.CACHE[path] = texture

        return texture

    @classmethod
    def __on_clean__(self):
        print(f"{consts.RUN_TIME:.5f} | ---- CLEANING TEXTURES ----")
        for texture in self.CACHE.values():
            print(f"{consts.RUN_TIME:.5f} |", texture._path)
            texture.clean(clean_func=True)
        for texture in self.NONE_FILE_CACHE.values():
            print(f"{consts.RUN_TIME:.5f} |", texture._uuid)
            texture.clean(clean_func=True)

    @classmethod
    def is_cached(self, texture: "Texture"):
        return texture in self.CACHE.values()

    @classmethod
    def cache_non_file(cls, texture: "Texture"):
        cls.NONE_FILE_CACHE[texture._uuid] = texture

    @classmethod
    def create_non_file_texture(
        cls,
        raw_image: pygame.Surface = None,
        width: int = 0,
        height: int = 0,
        channels: int = 4,
        color_buffer: bool = False,
        depth_buffer: bool = False,
        stencil_buffer: bool = False,
        is_tex: bool = False,
    ):
        if raw_image:
            texture = cls(raw_image=raw_image)
        elif color_buffer:
            texture = cls(
                special_args={
                    "width": width,
                    "height": height,
                    "channels": channels,
                    "type": "color",
                }
            )
        elif depth_buffer and stencil_buffer:
            texture = cls(
                special_args={
                    "width": width,
                    "height": height,
                    "channels": 1,
                    "type": "depth_stencil",
                }
            )
        elif depth_buffer and is_tex:
            texture = cls(
                special_args={
                    "width": width,
                    "height": height,
                    "channels": 1,
                    "type": "depth_texture",
                }
            )
        elif depth_buffer:
            texture = cls(
                special_args={
                    "width": width,
                    "height": height,
                    "channels": 1,
                    "type": "depth",
                }
            )
        elif stencil_buffer:
            texture = cls(
                special_args={
                    "width": width,
                    "height": height,
                    "channels": 1,
                    "type": "stencil",
                }
            )
        else:
            texture = cls(raw_image=pygame.Surface((width, height)).convert_alpha())
        cls.cache_non_file(texture)

        return texture

    @classmethod
    def terminate_specific_non_file_texture(cls, texture: "Texture"):
        texture.clean()
        cls.NONE_FILE_CACHE.pop(id(texture))

    # ------------------------------------------------------------------------ #

    def __init__(
        self,
        path: str = None,
        raw_image: pygame.Surface = None,
        special_args: dict = {},
        mipmap: bool = True,
        xflip: bool = False,
        yflip: bool = False,
    ):
        self._uuid = self.generate_texture_uuid()
        self._path = path
        self._raw_image = raw_image
        self._texture = None
        self._special_args = special_args
        self._has_mipmaps = mipmap

        self._xflip = xflip
        self._yflip = yflip

        # properties
        self._width = 0
        self._height = 0
        self._components = 0

        self._texture = None

        if self._special_args:
            self._width = self._special_args["width"]
            self._height = self._special_args["height"]
            self._components = self._special_args["channels"]

            if self._components < 1:
                print(__file__, "Invalid channel count")
                ctx.stop()

            if self._special_args["type"] == "depth":
                self._texture = consts.MGL_CONTEXT.depth_texture(
                    size=(self._width, self._height)
                )
            elif self._special_args["type"] == "depth_texture":
                self._texture = consts.MGL_CONTEXT.depth_texture(
                    size=(self._width, self._height)
                )
            elif self._special_args["type"] == "color":
                self._texture = consts.MGL_CONTEXT.texture(
                    size=(self._width, self._height), components=self._components
                )
            else:
                print(__file__, "Invalid special args: ", self._special_args)
                ctx.stop()

            # add to non file cache
            self.cache_non_file(self)
        else:
            self.__create(filepath=self._path is not None)

    def __create(self, filepath: bool = False):
        # check if valid string
        if self._path is not None and not self._path.split(".")[-1] in [
            "png",
            "jpg",
            "jpeg",
        ]:
            print(__file__, "Invalid texture file")
            ctx.stop()

        # retrieve data
        if self._path is not None:
            self._raw_image = consts.CTX_RESOURCE_MANAGER.load(self._path)
        self._width, self._height = self._raw_image.get_size()
        self._components = self._raw_image.get_bytesize()

        # create texture object
        self._texture = consts.MGL_CONTEXT.texture(
            size=(self._width, self._height),
            components=self._components,
            data=pygame.image.tostring(
                pygame.transform.flip(
                    self._raw_image, flip_y=self._yflip, flip_x=self._xflip
                ),
                "RGBA",
                False,
            ),
        )

        # create mipmaps
        if self._has_mipmaps:
            self._texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
            self._texture.build_mipmaps()

    # ------------------------------------------------------------------------ #
    # logic
    # ------------------------------------------------------------------------ #

    def clean(self, clean_func: bool = False):
        self._texture.release()

    def use(self, location: int = 0):
        self._texture.use(location=location)

    # ------------------------------------------------------------------------ #
    # special functions
    # ------------------------------------------------------------------------ #

    def __call__(self):
        return self._texture
