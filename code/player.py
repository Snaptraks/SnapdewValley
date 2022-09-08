import pygame

from settings import ROOT, LAYERS, PLAYER_TOOL_OFFSET
from soil import SoilLayer
from sprites import Tree, Interaction
from support import import_folder
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, ...],
        group: pygame.sprite.Group,
        collision_sprites: pygame.sprite.Group,
        tree_sprites: pygame.sprite.Group,
        interaction_sprites: pygame.sprite.Group,
        soil_layer: SoilLayer,
        toggle_shop,
    ) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = "down_idle"
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect: pygame.rect.Rect = self.image.get_rect(center=position)
        self.z = LAYERS["main"]

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

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

        # inventory
        self.item_inventory = {
            "wood": 20,
            "apple": 20,
            "corn": 20,
            "tomato": 20,
        }
        self.seed_inventory = {
            "corn": 5,
            "tomato": 5,
        }
        self.money = 200

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep: bool = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop

    def use_tool(self):
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                assert isinstance(tree, Tree)
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)

    def get_target_position(self) -> None:
        self.target_pos = (
            self.rect.center
            + PLAYER_TOOL_OFFSET[self.status.split("_")[0]]  # type: ignore
        )

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def import_assets(self) -> None:
        self.animations: dict[str, list[pygame.surface.Surface]] = {}

        for directory in (ROOT / "graphics/character").iterdir():
            self.animations[directory.name] = import_folder(directory)

    def animate(self, dt: float) -> None:
        self.frame_index += 4 * dt
        self.frame_index %= len(self.animations[self.status])
        self.image = self.animations[self.status][int(self.frame_index)]

    def _input(self) -> None:
        keys = pygame.key.get_pressed()

        if not self.timers["tool_use"].active and not self.sleep:
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

            if keys[pygame.K_RETURN]:
                self.toggle_shop()
                collided_interaction_sprite = pygame.sprite.spritecollide(
                    self, self.interaction_sprites, False
                )
                if collided_interaction_sprite:
                    collided_sprite = collided_interaction_sprite[0]
                    assert isinstance(collided_sprite, Interaction)
                    if collided_sprite.name == "Trader":
                        self.toggle_shop()

                    elif collided_sprite.name == "Bed":
                        self.status = "left_idle"
                        self.sleep = True

    def get_status(self) -> None:
        # idle
        if not self._is_moving():
            self.status = f"{self.status.split('_')[0]}_idle"

        if self.timers["tool_use"].active:
            self.status = f"{self.status.split('_')[0]}_{self.selected_tool}"

    def _is_moving(self) -> bool:
        return self.direction.length_squared() > 0

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction: str) -> None:
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, "hitbox"):
                if sprite.hitbox.colliderect(self.hitbox):  # type: ignore
                    if direction == "horizontal":
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left  # type: ignore
                        if self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right  # type: ignore
                        self.rect.centerx = self.pos.x = self.hitbox.centerx

                    if direction == "vertical":
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top  # type: ignore
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom  # type: ignore
                        self.rect.centery = self.pos.y = self.hitbox.centery

    def move(self, dt: float) -> None:
        # normalizing direction vector
        if self._is_moving():
            self.direction = self.direction.normalize()

        assert self.rect is not None
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision("horizontal")

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision("vertical")

    def update(self, dt: float) -> None:
        self._input()
        self.get_status()
        self.update_timers()
        self.get_target_position()
        self.move(dt)
        self.animate(dt)
