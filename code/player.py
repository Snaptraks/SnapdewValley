import pygame

from settings import ROOT
from support import import_folder
from timer import Timer


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

        # timers
        self.timers = {
            "tool_use": Timer(350, self.use_tool),
            "tool_switch": Timer(200),
            "seed_use": Timer(350, self.use_seed),
            "seed_switch": Timer(200),
        }

        # tools
        self.tools = ["hoe", "axe", "water"]
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds
        self.seeds = ["corn", "tomato"]
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self):
        ...

    def use_seed(self):
        ...

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

        if not self.timers["tool_use"].active:
            # directions
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

            # tool use
            if keys[pygame.K_SPACE]:
                # timer for the tool use
                self.timers["tool_use"].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change tool
            if keys[pygame.K_q] and not self.timers["tool_switch"].active:
                self.timers["tool_switch"].activate()
                self.tool_index += 1
                self.tool_index %= len(self.tools)
                self.selected_tool = self.tools[self.tool_index]

            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers["seed_use"].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change seed
            if keys[pygame.K_e] and not self.timers["seed_switch"].active:
                self.timers["seed_switch"].activate()
                self.seed_index += 1
                self.seed_index %= len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]

    def get_status(self):
        # idle
        if not self._is_moving():
            self.status = f"{self.status.split('_')[0]}_idle"

        if self.timers["tool_use"].active:
            self.status = f"{self.status.split('_')[0]}_{self.selected_tool}"

    def _is_moving(self) -> bool:
        return self.direction.length_squared() > 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

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
        self.update_timers()
        self.move(dt)
        self.animate(dt)
