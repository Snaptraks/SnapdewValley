import random

import pygame
from pytmx.util_pygame import load_pygame

from menu import Menu
from player import Player
from overlay import Overlay
from sky import Rain, Sky
from soil import SoilLayer, Plant
from support import import_folder
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
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
        self.raining: bool = random.randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # shop
        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        # music
        self.success = pygame.mixer.Sound(ROOT / "audio/success.wav")
        self.success.set_volume(0.3)

        self.music = pygame.mixer.Sound(ROOT / "audio/music.mp3")
        self.music.set_volume(0.2)
        self.music.play(loops=-1)

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
                    toggle_shop=self.toggle_shop,
                )

            if obj.name in ("Bed", "Trader"):
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
        self.success.play()

    def toggle_shop(self) -> None:
        self.shop_active = not self.shop_active

    def reset(self):
        # plants
        self.soil_layer.update_plants()

        # soil
        self.soil_layer.remove_water()

        # randomize the rain
        self.raining = random.randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # apples on the trees
        for tree in self.tree_sprites.sprites():
            assert isinstance(tree, Tree)
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # sky
        self.sky.start_color = [255] * 3

    def plant_collision(self) -> None:
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                assert isinstance(plant, Plant)
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(
                        position=plant.rect.topleft,
                        surface=plant.image,  # type: ignore
                        groups=self.all_sprites,
                        z=LAYERS["main"],
                    )
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][
                        plant.rect.centerx // TILE_SIZE
                    ].remove("P")

    def run(self, dt: float) -> None:

        # drawing logic
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)

        # updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        # weather
        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update()

        self.sky.display(dt)

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
