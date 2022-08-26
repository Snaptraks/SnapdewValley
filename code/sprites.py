import pygame
from settings import LAYERS


class Generic(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        z: int = LAYERS["main"],
    ) -> None:
        super().__init__(groups)  # type: ignore
        self.image = surface
        self.rect: pygame.rect.Rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


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


class Tree(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group | list[pygame.sprite.Group],
        name: str,
    ) -> None:
        super().__init__(position, surface, groups)
