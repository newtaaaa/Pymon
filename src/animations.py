import pygame


class AnimateSprite(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.speed = 1
        self.clock = 0
        self.anim_index = 0
        self.scale = 0.7
        if name != "player":
            self.sprite_sheet = pygame.image.load(f"img/pnj/{name}.png")
        else:
            self.sprite_sheet = pygame.image.load(f"img/player/idle/0.png")
        self.images = {
            "down": self.get_images(0),
            "left": self.get_images(32),
            "right": self.get_images(64),
            "up": self.get_images(96)
        }

    def get_image(self, x, y):
        image = pygame.Surface([32, 32], pygame.SRCALPHA)  # support de transparence
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def get_images(self, y):
        images = []
        for i in range(0, 3):
            x = i*32
            image = self.get_image(x, y)
            image = pygame.transform.scale(image, (int(32 * self.scale), int(32 * self.scale)))
            images.append(image)
        return images

    def change_animation(self, name):
        self.image = self.images[name][self.anim_index]
        self.image.set_colorkey([0, 0, 0])
        self.clock += self.speed*8

        if self.clock >= 100:
            self.anim_index += 1
            if self.anim_index >= len(self.images[name]):
                self.anim_index = 0
            self.clock = 0
