import pygame
import random

# --- New TrailParticle Class ---
class TrailParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y + 14
        self.color = color
        self.radius = 5
        self.alpha = 255
        self.alpha_decay = 5
        self.vel_y = random.uniform(-1, -0.5)
        self.vel_x = random.uniform(-0.5, 0.5)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1

        self.alpha -= self.alpha_decay
        self.radius -= 0.1

    def draw(self, screen):
        if self.alpha > 0 and self.radius > 0:
            s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], int(self.alpha)), (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(s, (self.x - self.radius, self.y - self.radius))


def get_frames(sheet, frame_width, frame_height, scale=5):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
            frames.append(frame)
    return frames


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=5):
        super().__init__()
        self.was_on_ground = False

        # 👇 Load sounds here instead of top-level
        self.jump_sound = pygame.mixer.Sound("jump.mp3")

        # --- Load animations ---
        idle_sheet = pygame.image.load("Idle.png[1].png").convert_alpha()
        run_sheet = pygame.image.load("Run.png").convert_alpha()

        idle_width = idle_sheet.get_width() // 3
        idle_height = idle_sheet.get_height()
        run_width = run_sheet.get_width() // 8
        run_height = run_sheet.get_height()

        self.animations = {
            "idle": get_frames(idle_sheet, idle_width, idle_height, scale),
            "run": get_frames(run_sheet, run_width, run_height, scale),
        }

        self.state = "idle"
        self.current_frame = 0
        self.image = self.animations[self.state][self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.animation_speed = 120

        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        # --- New: Trail particle list ---
        self.trail_particles = []
    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.current_frame = 0
            self.animation_timer = 0
        

    def update(self, keys, platforms):
        moving = False
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.facing_right = True
            moving = True

        if moving:
            self.set_state("run")
            self.trail_particles.append(TrailParticle(self.rect.centerx, self.rect.centery, (255, 255, 255)))
        else:
            self.set_state("idle")

        dt = pygame.time.get_ticks()
        if dt - self.animation_timer > self.animation_speed:
            self.animation_timer = dt
            frames = self.animations[self.state]
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

        self.vel_y += 1
        self.rect.y += self.vel_y

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
        # --- Landing check goes here ---
        landed = not self.was_on_ground and self.on_ground
        self.was_on_ground = self.on_ground

        # if landed:
        #     for i in range(10):  # number of mud particles
        #         particles.append(Particle(self.rect.centerx, self.rect.bottom))

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -21
            self.on_ground = False
            self.jump_sound.play()

