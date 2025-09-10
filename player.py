import pygame

#idle = pygame.image.load("Idle.png.png").convert_alpha()
pygame.mixer.init()


def get_frames(sheet, frame_width, frame_height):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
    
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frames.append(frame)
    
        return frames

#player_frames = get_frames(idle, 8, 8)




class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=5):
        super().__init__()
        
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        

    
    def update(self, keys, platforms):
        # Example movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -21
            
