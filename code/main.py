import sys

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from level import Level


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snapdew Valley")
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
