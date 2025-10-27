import pygame
import os
from src.animations import AnimateSprite


class Entity(AnimateSprite):
    def __init__(self, name, x, y):
        super().__init__(name)
        self.position = [x, y]
        self.name = name
        if name != "player":
            self.image = self.get_image(0, 0)
            self.image.set_colorkey([0, 0, 0])
            self.rect = self.image.get_rect(topleft=self.position)
            self.feet = pygame.Rect(0, 0, self.rect.width * 0.8, 20)
        else:
            self.image = pygame.image.load(f"img/player/idle/0.png")
        self.update_time = pygame.time.get_ticks()
        self.old_position = self.position.copy()

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def save_location(self):
        self.old_position = self.position.copy()

    def get(self):
        self.image = self.images["down"]
        self.image.set_colorkey([0, 0, 0])
        return self.image

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        image = pygame.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image


class Player(Entity):
    def __init__(self):
        super().__init__("player", 0, 0)
        self.step_count = 0
        self.flip = False
        self.last_direction = 0
        self.speed = 1
        self.scale = 0.8
        self.index = 0
        self.action = 0
        self.images = []
        self.direction = 0
        animation_list = ['bottom', 'top', 'run', 'idle']
        for animation in animation_list:
            temp_list = []
            num_frames = len(os.listdir(f"img/player/{animation}"))
            for num in range(num_frames):
                image = pygame.image.load(f"img/player/{animation}/{num}.png").convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * self.scale),
                                                       int(image.get_height() * self.scale)))
                temp_list.append(image)
            self.images.append(temp_list)
        self.image = self.images[self.action][self.index]
        self.rect = self.image.get_rect(topleft=self.position)
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        # À remplir dans les classes filles

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self, left, right, down, up):
        dx = 0
        dy = 0

        if left and not down and not up:
            dx = -self.speed
            self.flip = True
            self.direction = 2

        if right and not down and not up:
            dx = self.speed
            self.flip = False
            self.direction = 2

        if down and not right and not left:
            dy = self.speed
            self.direction = 0

        if up and not right and not left:
            dy = -self.speed
            self.direction = 1

        self.position[0] += dx
        self.position[1] += dy

        if not right and not left and not down and not up:
            self.update_action(3)  # idle
        else:
            self.last_direction = self.direction
            self.update_action(self.direction)

    def update_animation(self):
        animation_cooldown = 120
        action_to_display = self.last_direction if self.action == 3 else self.action
        image = self.images[action_to_display][self.index]
        self.image = pygame.transform.flip(image, self.flip, False)
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
        if self.index >= len(self.images[self.action]):
            if self.action == 3:
                self.index = len(self.images[self.action]) - 1
            else:
                self.index = 0


class NPC(Entity):
    def __init__(self, name, nb_points, dialog):
        super().__init__(name, 0, 0)
        self.nb_points = nb_points
        self.points = []
        self.name = name
        self.current_point = 0
        self.speed = 1
        self.dialog = dialog

    def move_right(self):
        self.change_animation("right")
        self.position[0] += self.speed

    def move_left(self):
        self.change_animation("left")
        self.position[0] -= self.speed

    def move_up(self):
        self.change_animation("up")
        self.position[1] -= self.speed

    def move_down(self):
        self.change_animation("down")
        self.position[1] += self.speed

    def teleport_spawn(self):
        location = self.points[self.current_point]
        self.position[0] = location.x
        self.position[1] = location.y
        self.save_location()

    def load_points(self, tmx_data):
        for num in range(1, self.nb_points+1):
            point = tmx_data.get_object_by_name(f"{self.name}_path{num}")
            rect = pygame.Rect(point.x, point.y, point.width, point.height)
            self.points.append(rect)

    def move(self):
        current_point = self.current_point
        target_point = self.current_point + 1

        if target_point >= self.nb_points:
            target_point = 0
        current_rect = self.points[current_point]
        target_rect = self.points[target_point]
        if current_rect.y < target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_down()
        elif current_rect.y > target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_up()
        elif current_rect.x > target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_left()
        elif current_rect.x < target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_right()

        if self.rect.colliderect(target_rect):
            self.current_point = target_point
