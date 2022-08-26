import pygame
from pytmx.util_pygame import load_pygame

from player import Player
from overlay import Overlay
from support import import_folder
from sprites import Generic, Water, WildFlower, Tree
from settings import ROOT, SCREEN_HEIGHT, SCREEN_WIDTH, LAYERS, TILE_SIZE


class Level:
    def __init__(self) -> None:
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self) -> None:
        tmx_data = load_pygame(str(ROOT / "data/map.tmx"))

        # house
        for layer in ("HouseFloor", "HouseFurnitureBottom"):
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surface,
                    self.all_sprites,
                    LAYERS["house_bottom"],
                )

        for layer in ("HouseWalls", "HouseFurnitureTop"):
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surface,
                    self.all_sprites,
                )

        # fence
        for x, y, surface in tmx_data.get_layer_by_name("Fence").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                surface,
                self.all_sprites,
            )

        # water
        water_frames = import_folder(ROOT / "graphics/water")
        for x, y, surface in tmx_data.get_layer_by_name("Water").tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree((obj.x, obj.y), obj.image, self.all_sprites, name=obj.name)

        # wildflowers
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower((obj.x, obj.y), obj.image, self.all_sprites)

        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.all_sprites)
        Generic(
            position=(0, 0),
            surface=pygame.image.load(
                ROOT / "graphics/world/ground.png"
            ).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["ground"],
        )

    def run(self, dt: float) -> None:
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player: Player) -> None:
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        sprites = sorted(self.sprites(), key=lambda s: (s.z, s.rect.centery))  # type: ignore # noqa
        for sprite in sprites:
            offset_rect = sprite.rect.copy()  # type:ignore
            offset_rect.center -= self.offset  # type: ignore
            self.display_surface.blit(sprite.image, offset_rect)  # type: ignore
