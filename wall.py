import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(250, 250, 250)):
        super().__init__()
        # Create surface for wall
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # Rectangle for position & collisions
        self.rect = self.image.get_rect(topleft=(x, y))