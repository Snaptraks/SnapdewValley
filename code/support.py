from pathlib import Path

import pygame


def import_folder(path: Path) -> list:
    surface_list = []

    for file in path.iterdir():
        image_surface = pygame.image.load(file).convert_alpha()
        surface_list.append(image_surface)

    return surface_list


def import_folder_dict(path: Path) -> dict[str, pygame.surface.Surface]:
    surface_dict: dict[str, pygame.surface.Surface] = {}

    for file in path.iterdir():
        image_surface = pygame.image.load(file).convert_alpha()
        surface_dict[file.stem] = image_surface

    return surface_dict
