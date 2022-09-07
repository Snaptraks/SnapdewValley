from typing import Callable

import pygame

from player import Player
from timer import Timer
from settings import ROOT, SCREEN_HEIGHT, SCREEN_WIDTH


class Menu:
    def __init__(self, player: Player, toggle_menu: Callable[[], None]) -> None:
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(ROOT / "font/LycheeSoda.ttf", 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory.keys()) + list(
            self.player.seed_inventory.keys()
        )
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        # movement
        self.index = 0
        self.timer = Timer(200)

    def display_money(self) -> None:
        text_surface = self.font.render(f"{self.player.money}$", False, "Black")
        text_rect = text_surface.get_rect(
            midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20)
        )
        pygame.draw.rect(self.display_surface, "White", text_rect.inflate(10, 10), 0, 6)
        self.display_surface.blit(text_surface, text_rect)

    def setup(self) -> None:
        # text surfaces
        self.text_surfaces = []
        self.total_height = 0
        for item in self.options:
            text_surface = self.font.render(item.title(), False, "Black")
            self.text_surfaces.append(text_surface)
            self.total_height += text_surface.get_height() + 2 * self.padding

        self.total_height += (len(self.text_surfaces) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height,
        )

    def _input(self) -> None:
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

        # limit the values
        self.index = min(len(self.options), max(0, self.index))

    def show_entry(
        self,
        text_surface: pygame.surface.Surface,
        amount: int,
        top: int,
        selected: bool,
    ) -> None:
        # background
        bg_rect = pygame.Rect(
            self.main_rect.left,
            top,
            self.width,
            text_surface.get_height() + 2 * self.padding,
        )
        pygame.draw.rect(self.display_surface, "White", bg_rect, 0, 6)

        # text
        text_rect = text_surface.get_rect(
            midleft=(self.main_rect.left + 20, bg_rect.centery)
        )
        self.display_surface.blit(text_surface, text_rect)

        # amount
        amount_surface = self.font.render(f"{amount}", False, "Black")
        amount_rect = amount_surface.get_rect(
            midright=(self.main_rect.right - 20, bg_rect.centery)
        )
        self.display_surface.blit(amount_surface, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, "black", bg_rect, 4, 6)

    def update(self) -> None:
        self._input()
        self.display_money()
        for i, text_surface in enumerate(self.text_surfaces):
            top: int = self.main_rect.top + i * (
                text_surface.get_height() + 2 * self.padding + self.space
            )
            amount_list = list(self.player.item_inventory.values()) + list(
                self.player.seed_inventory.values()
            )
            self.show_entry(text_surface, amount_list[i], top, i == self.index)
