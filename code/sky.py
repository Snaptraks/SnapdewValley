import random
import pygame

from sprites import Generic
from support import import_folder
from settings import ROOT, LAYERS, SCREEN_WIDTH, SCREEN_HEIGHT


class Sky:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255] * 3
        self.end_color = [38, 101, 189]

    def display(self, dt: float) -> None:
        for i, value in enumerate(self.end_color):
            if self.start_color[i] > value:
                self.start_color[i] -= 2 * dt  # type: ignore

        self.full_surface.fill(self.start_color)
        self.display_surface.blit(
            self.full_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )


class Drop(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        moving: bool,
        z: int = ...,
    ) -> None:
        super().__init__(position, surface, groups, z)

        # general setup
        self.lifetime = random.randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.position = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = random.randint(200, 250)

    def update(self, dt: float) -> None:
        # movement
        if self.moving:
            self.position += self.direction * self.speed * dt
            self.rect.topleft = (round(self.position.x), round(self.position.y))

        # timer
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(ROOT / "graphics/rain/drops")
        self.rain_floor = import_folder(ROOT / "graphics/rain/floor")
        self.floor_w, self.floor_h = pygame.image.load(
            ROOT / "graphics/world/ground.png"
        ).get_size()

    def create_floor(self) -> None:
        Drop(
            position=(random.randint(0, self.floor_w), random.randint(0, self.floor_h)),
            surface=random.choice(self.rain_floor),
            groups=self.all_sprites,
            moving=False,
            z=LAYERS["rain_floor"],
        )

    def create_drops(self) -> None:
        Drop(
            position=(random.randint(0, self.floor_w), random.randint(0, self.floor_h)),
            surface=random.choice(self.rain_drops),
            groups=self.all_sprites,
            moving=True,
            z=LAYERS["rain_drops"],
        )

    def update(self) -> None:
        self.create_floor()
        self.create_drops()
