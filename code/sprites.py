from random import randint, choice

import pygame

from timer import Timer
from settings import ROOT, LAYERS, APPLE_POS


class Generic(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        z: int = LAYERS["main"],
    ) -> None:
        super().__init__(groups)  # type: ignore
        self.image: pygame.surface.Surface = surface
        self.rect: pygame.rect.Rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


class Interaction(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        size: tuple[int, ...],
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        name: str,
    ) -> None:
        surface = pygame.Surface(size)
        super().__init__(position, surface, groups)
        self.name = name


class Water(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        frames: list[pygame.surface.Surface],
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
    ) -> None:
        # animation setup
        self.frames = frames
        self.frame_index: float = 0

        # sprite setup
        super().__init__(
            position, self.frames[self.frame_index], groups, LAYERS["water"]
        )

    def animate(self, dt: float):
        self.frame_index += 5 * dt
        self.frame_index %= len(self.frames)
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt: float):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
    ) -> None:
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        z: int = LAYERS["main"],
        duration: int = 200,
    ) -> None:
        super().__init__(position, surface, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        # white surface
        mask_surface = pygame.mask.from_surface(self.image)
        new_surface = mask_surface.to_surface()
        new_surface.set_colorkey((0, 0, 0))
        self.image = new_surface

    def update(self, dt: float):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        name: str,
        player_add,
    ) -> None:
        super().__init__(position, surface, groups)

        # tree attributes
        self.health: int = 5
        self.alive: bool = True
        self.stump_surface = pygame.image.load(
            ROOT / f"graphics/stumps/{name.lower()}.png"
        ).convert_alpha()
        self.invul_timer = Timer(200)

        # apples
        self.apple_surface = pygame.image.load(ROOT / "graphics/fruit/apple.png")
        self.apple_positions = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def damage(self) -> None:
        # damaging the tree
        self.health -= 1

        # remove an apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                random_apple.rect.topleft,
                random_apple.image,
                self.groups()[0],
                z=LAYERS["fruit"],
            )
            self.player_add("apple")
            random_apple.kill()

    def check_death(self) -> None:
        if self.health <= 0:
            Particle(
                self.rect.topleft,
                self.image,
                self.groups()[0],
                LAYERS["fruit"],
                300,
            )
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add("wood")

    def update(self, dt: float) -> None:
        if self.alive:
            self.check_death()

    def create_fruit(self) -> None:
        for pos in self.apple_positions:
            if randint(0, 10) < 2:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                Generic(
                    (x, y),
                    self.apple_surface,
                    [self.apple_sprites, self.groups()[0]],  # type: ignore
                    z=LAYERS["fruit"],
                )
