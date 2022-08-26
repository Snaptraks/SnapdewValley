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
