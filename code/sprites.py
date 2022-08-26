import pygame
from settings import LAYERS


class Generic(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group,
        z: int = LAYERS["main"],
    ) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = z


class Water(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        frames: list[pygame.surface.Surface],
        groups: pygame.sprite.Group,
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
        groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(position, surface, groups)


class Tree(Generic):
    def __init__(
        self,
        position: tuple[int, ...],
        surface: pygame.surface.Surface,
        groups: pygame.sprite.Group,
        name: str,
    ) -> None:
        super().__init__(position, surface, groups)
