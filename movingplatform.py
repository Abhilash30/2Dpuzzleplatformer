import pygame

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, range_x=0, range_y=0, speed=2):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((225, 225, 0))  # yellow platform
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement settings
        self.start_x, self.start_y = x, y
        self.range_x = range_x
        self.range_y = range_y
        self.speed = speed
        self.direction_x = 1 if range_x > 0 else 0
        self.direction_y = 1 if range_y > 0 else 0

    def update(self):
        # Horizontal movement
        if self.direction_x != 0:
            self.rect.x += self.speed * self.direction_x
            if abs(self.rect.x - self.start_x) >= self.range_x:
                self.direction_x *= -1  # reverse direction

        # Vertical movement
        if self.direction_y != 0:
            self.rect.y += self.speed * self.direction_y
            if abs(self.rect.y - self.start_y) >= self.range_y:
                self.direction_y *= -1
