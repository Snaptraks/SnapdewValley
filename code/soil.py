import random
from typing import Callable

import pygame
from pytmx.util_pygame import load_pygame

from support import import_folder, import_folder_dict
from settings import ROOT, TILE_SIZE, LAYERS, GROW_SPEED


class SoilTile(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
    ) -> None:
        super().__init__(groups)  # type: ignore
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS["soil"]


class WaterTile(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
    ) -> None:
        super().__init__(groups)  # type: ignore
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = LAYERS["soil_water"]


class Plant(pygame.sprite.Sprite):
    def __init__(
        self,
        plant_type: str,
        soil: SoilTile,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        check_watered: Callable[[tuple[int, ...]], bool],
    ) -> None:
        super().__init__(groups)  # type: ignore

        # setup
        self.plant_type = plant_type
        self.frames = import_folder(ROOT / "graphics/fruit" / plant_type)
        self.soil = soil
        self.check_watered = check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable: bool = False

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == "corn" else -8
        self.rect: pygame.rect.Rect = self.image.get_rect(
            midbottom=(
                self.soil.rect.midbottom  # type: ignore
                + pygame.math.Vector2(0, self.y_offset)  # type: ignore
            )
        )
        self.z = LAYERS["ground_plant"]

    def grow(self) -> None:
        if self.check_watered(self.rect.center):  # type: ignore
            self.age += self.grow_speed

            if self.age >= 1:
                self.z = LAYERS["main"]
                rect = self.rect
                assert isinstance(rect, pygame.rect.Rect)
                self.hitbox = rect.copy().inflate(-26, rect.height * 0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(
                midbottom=(
                    self.soil.rect.midbottom  # type: ignore
                    + pygame.math.Vector2(0, self.y_offset)  # type: ignore
                )
            )


class SoilLayer:
    def __init__(
        self, all_sprites: pygame.sprite.Group, collision_sprites: pygame.sprite.Group
    ) -> None:
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfaces = import_folder_dict(ROOT / "graphics/soil")
        self.water_surfaces = import_folder(ROOT / "graphics/soil_water")

        self.create_soil_grid()
        self.create_hit_rects()

        # rain
        self.raining: bool

    def create_soil_grid(self) -> None:
        ground = pygame.image.load(ROOT / "graphics/world/ground.png")
        h_tiles, v_tiles = (
            ground.get_width() // TILE_SIZE,
            ground.get_height() // TILE_SIZE,
        )
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in (
            load_pygame(str(ROOT / "data/map.tmx"))
            .get_layer_by_name("Farmable")
            .tiles()
        ):
            self.grid[y][x].append("F")

    def create_hit_rects(self) -> None:
        self.hit_rects: list[pygame.Rect] = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if "F" in cell:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point: tuple[float, ...]) -> None:
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if "F" in self.grid[y][x]:
                    self.grid[y][x].append("X")
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, point: tuple[float, ...]) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):  # type: ignore
                rect = soil_sprite.rect
                assert isinstance(rect, pygame.rect.Rect)
                # add entry to the soil grid -> "W"
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                self.grid[y][x].append("W")

                # create a water sprite
                WaterTile(
                    position=(rect.x, rect.y),
                    surface=random.choice(self.water_surfaces),
                    groups=[self.all_sprites, self.water_sprites],
                )

    def water_all(self) -> None:
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if "X" in cell and "W" not in cell:
                    cell.append("W")
                    WaterTile(
                        position=(j * TILE_SIZE, i * TILE_SIZE),
                        surface=random.choice(self.water_surfaces),
                        groups=[self.all_sprites, self.water_sprites],
                    )

    def remove_water(self) -> None:
        # destroy all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # clean up the grid
        for row in self.grid:
            for cell in row:
                if "W" in cell:
                    cell.remove("W")

    def check_watered(self, position: tuple[int, ...]) -> bool:
        x = position[0] // TILE_SIZE
        y = position[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = "W" in cell
        return is_watered

    def plant_seed(self, point: tuple[float, ...], seed) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            assert isinstance(soil_sprite, SoilTile)
            if soil_sprite.rect.collidepoint(point):  # type: ignore
                rect = soil_sprite.rect
                assert isinstance(rect, pygame.rect.Rect)
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if "P" not in self.grid[y][x]:
                    self.grid[y][x].append("P")
                    Plant(
                        plant_type=seed,
                        soil=soil_sprite,
                        groups=[
                            self.all_sprites,
                            self.plant_sprites,
                            self.collision_sprites,
                        ],
                        check_watered=self.check_watered,
                    )

    def update_plants(self) -> None:
        for plant in self.plant_sprites.sprites():
            assert isinstance(plant, Plant)
            plant.grow()

    def create_soil_tiles(self) -> None:
        self.soil_sprites.empty()
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if "X" in cell:

                    # tile options
                    t = "X" in self.grid[i - 1][j]
                    b = "X" in self.grid[i + 1][j]
                    r = "X" in row[j + 1]
                    l = "X" in row[j - 1]  # noqa: E741

                    tile_type = "o"

                    # all_sides
                    if all([t, b, r, l]):
                        tile_type = "x"

                    # horizontal only
                    if l and not any([t, r, b]):
                        tile_type = "r"
                    if r and not any([t, l, b]):
                        tile_type = "l"
                    if r and l and not any([t, b]):
                        tile_type = "lr"

                    # vertical only
                    if t and not any([r, l, b]):
                        tile_type = "b"
                    if b and not any([r, l, t]):
                        tile_type = "t"
                    if b and t and not any([l, r]):
                        tile_type = "tb"

                    # corners
                    if l and b and not any([t, r]):
                        tile_type = "tr"
                    if r and b and not any([t, l]):
                        tile_type = "tl"
                    if l and t and not any([b, r]):
                        tile_type = "br"
                    if r and t and not any([b, l]):
                        tile_type = "bl"

                    # T shapes
                    if all([t, b, r]) and not l:
                        tile_type = "tbr"
                    if all([t, b, l]) and not r:
                        tile_type = "tbl"
                    if all([l, r, t]) and not b:
                        tile_type = "lrb"
                    if all([l, r, b]) and not t:
                        tile_type = "lrt"

                    SoilTile(
                        position=(j * TILE_SIZE, i * TILE_SIZE),
                        surface=self.soil_surfaces[tile_type],
                        groups=[self.all_sprites, self.soil_sprites],
                    )
