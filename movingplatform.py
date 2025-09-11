import pygame

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, dx=2, dy=0, move_range=100):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((250, 250, 250))  # WHITE
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement setup
        self.start_pos = pygame.Vector2(x, y)
        self.dx = dx   # Horizontal speed
        self.dy = dy   # Vertical speed
        self.move_range = move_range
        self.direction = 1

    def update(self):
        # Move
        self.rect.x += self.dx * self.direction
        self.rect.y += self.dy * self.direction

        # Reverse direction when past range
        if abs(self.rect.x - self.start_pos.x) > self.move_range:
            self.direction *= -1
        if abs(self.rect.y - self.start_pos.y) > self.move_range:
            self.direction *= -1