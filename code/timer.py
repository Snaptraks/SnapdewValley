import pygame
from typing import Callable


class Timer:
    def __init__(self, duration: int, func: Callable | None = None) -> None:
        self.duration = duration
        self.func = func
        self.start_time: int = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.deactivate()
            if self.func is not None:
                self.func()
