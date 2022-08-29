from typing import Callable

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Transition:
    def __init__(self, reset: Callable, player) -> None:
        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):

        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()

        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed *= -1

        self.image.fill((self.color,) * 3)
        self.display_surface.blit(
            self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
