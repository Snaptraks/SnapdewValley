import pygame
from player import Player
from settings import ROOT, OVERLAY_POSITIONS

OVERLAY_PATH = ROOT / "graphics/overlay"


class Overlay:
    def __init__(self, player: Player) -> None:
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # imports
        self.tools_surface = {
            tool: pygame.image.load(OVERLAY_PATH / f"{tool}.png").convert_alpha()
            for tool in self.player.tools
        }
        self.seeds_surface = {
            seed: pygame.image.load(OVERLAY_PATH / f"{seed}.png").convert_alpha()
            for seed in self.player.seeds
        }

    def display(self) -> None:
        # tool
        tool_surface = self.tools_surface[self.player.selected_tool]
        tool_rectangle = tool_surface.get_rect(midbottom=OVERLAY_POSITIONS["tool"])
        self.display_surface.blit(tool_surface, tool_rectangle)

        # seed
        seed_surface = self.seeds_surface[self.player.selected_seed]
        seed_rectangle = seed_surface.get_rect(midbottom=OVERLAY_POSITIONS["seed"])
        self.display_surface.blit(seed_surface, seed_rectangle)
