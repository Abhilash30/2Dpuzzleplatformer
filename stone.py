# stone.py
import pygame

class Stone(pygame.sprite.Sprite):
    def __init__(self, x, y, size=20, color=(1, 1, 1)):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        # Move stone by its velocity
        self.rect.x += int(self.velocity.x)
        self.rect.y += int(self.velocity.y)

        # Friction slows it down
        self.velocity *= 0.85
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        if abs(self.velocity.y) < 0.1:
            self.velocity.y = 0

    def push(self, dx, dy):
        # Add velocity when player collides
        self.velocity.x += dx * 0.5
        self.velocity.y += dy * 0.5