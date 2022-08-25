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

    def animate(self, dt: float) -> None:
        self.frame_index += 4 * dt
        self.frame_index %= len(self.animations[self.status])
        self.image = self.animations[self.status][int(self.frame_index)]

    def _input(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.status = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.status = "down"
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = "right"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = "left"
        else:
            self.direction.x = 0

    def get_status(self):
        # idle
        if not self._is_moving():
            self.status = f"{self.status.split('_')[0]}_idle"

    def _is_moving(self) -> bool:
        return self.direction.length_squared() > 0

    def move(self, dt: float):
        # normalizing direction vector
        if self._is_moving():
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        if self.rect is not None:
            self.rect.centerx = int(self.pos.x)

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        if self.rect is not None:
            self.rect.centery = int(self.pos.y)

    def update(self, dt: float) -> None:
        self._input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
