import pygame
from pytmx.util_pygame import load_pygame

from settings import ROOT, TILE_SIZE, LAYERS


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


class SoilLayer:
    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surface = pygame.image.load(ROOT / "graphics/soil/o.png")

        # requirements
        # if the area is farmable
        # if the soil has been watered
        # if the soil has a plant
        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
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

    def create_hit_rects(self):
        self.hit_rects: list[pygame.Rect] = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if "F" in cell:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point: tuple[float, ...]):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if "F" in self.grid[y][x]:
                    self.grid[y][x].append("X")
                    self.create_soil_tiles()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if "X" in cell:
                    SoilTile(
                        position=(j * TILE_SIZE, i * TILE_SIZE),
                        surface=self.soil_surface,
                        groups=[self.all_sprites, self.soil_sprites],
                    )
