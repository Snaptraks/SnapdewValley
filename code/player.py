import pygame

from settings import ROOT
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, ...], group: pygame.sprite.Group) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = "down_idle"
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self) -> None:
        self.animations: dict[str, list] = {}

        for directory in (ROOT / "graphics/character").iterdir():
            self.animations[directory.name] = import_folder(directory)

    def _input(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, dt: float):
        # normalizing direction vector
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        if self.rect is not None:
            self.rect.centerx = int(self.pos.x)

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        if self.rect is not None:
            self.rect.centery = int(self.pos.y)

    def update(self, dt: float):
        self._input()
        self.move(dt)
