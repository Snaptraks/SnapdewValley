from pathlib import Path

import pygame


def import_folder(path: Path) -> list:
    surface_list = []

    for file in path.iterdir():
        image_surface = pygame.image.load(file).convert_alpha()
        surface_list.append(image_surface)

    return surface_list
