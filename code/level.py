import random

import pygame
from pytmx.util_pygame import load_pygame

from player import Player
from overlay import Overlay
from sky import Rain
from soil import SoilLayer
from support import import_folder
from sprites import Generic, Water, WildFlower, Tree, Interaction
from transition import Transition
from settings import (
    ROOT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    LAYERS,
    TILE_SIZE,
)


class Level:
    def __init__(self) -> None:
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining: bool = random.randint(0, 10) > 3
        self.soil_layer.raining = self.raining

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
                [self.all_sprites, self.collision_sprites],
            )

        # water
        water_frames = import_folder(ROOT / "graphics/water")
        for x, y, surface in tmx_data.get_layer_by_name("Water").tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree(
                position=(obj.x, obj.y),
                surface=obj.image,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add,
            )

        # wildflowers
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower(
                (obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites]
            )

        # collision tiles
        for x, y, surface in tmx_data.get_layer_by_name("Collision").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),
                self.collision_sprites,
            )

        # Player
        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                self.player = Player(
                    position=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                )

            if obj.name == "Bed":
                Interaction(
                    position=(obj.x, obj.y),
                    size=(obj.width, obj.height),
                    groups=self.interaction_sprites,
                    name=obj.name,
                )

        Generic(
            position=(0, 0),
            surface=pygame.image.load(
                ROOT / "graphics/world/ground.png"
            ).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["ground"],
        )

    def player_add(self, item):
        self.player.item_inventory[item] += 1

    def reset(self):
        # plants
        self.soil_layer.update_plants()

        # soil
        self.soil_layer.remove_water()

        # randomize the rain
        self.raining = random.randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # apples on the trees
        for tree in self.tree_sprites.sprites():
            assert isinstance(tree, Tree)
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def run(self, dt: float) -> None:
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()

        # rain
        if self.raining:
            self.rain.update()

        # transition overlay
        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player: Player) -> None:
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        sprites = sorted(
            self.sprites(), key=lambda s: (s.z, s.rect.centery)  # type: ignore
        )
        for sprite in sprites:
            offset_rect = sprite.rect.copy()  # type:ignore
            offset_rect.center -= self.offset  # type: ignore
            self.display_surface.blit(sprite.image, offset_rect)  # type: ignore
