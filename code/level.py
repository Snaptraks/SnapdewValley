import pygame

from player import Player
from overlay import Overlay
from sprites import Generic
from settings import ROOT, SCREEN_HEIGHT, SCREEN_WIDTH, LAYERS


class Level:
    def __init__(self) -> None:
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self) -> None:
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

        sprites = sorted(self.sprites(), key=lambda s: s.z)  # type: ignore
        for sprite in sprites:
            offset_rect = sprite.rect.copy()  # type:ignore
            offset_rect.center -= self.offset  # type: ignore
            self.display_surface.blit(sprite.image, offset_rect)  # type: ignore
