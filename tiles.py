import pygame, pytmx
from player import Player
from stone import Stone
import lvl2  # Level-2 module
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from movingplatform import MovingPlatform

# ---------------------- ML Setup ----------------------
# Dummy training data: [death_lvl1, time_lvl1, death_lvl2, time_lvl2]
X_train = np.array([
    [3, 120, 1, 90],
    [1, 80, 2, 110],
    [0, 60, 0, 70]
])
y_train = np.array([2, 1, 2])  # 1 or 2 → level to assign

model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# ---------------------- Level Loader ----------------------
def run_level(level_file, background_file):
    """
    Generic Level Runner: handles platforms, stones, player movement,
    deaths, timer, doors. Returns death_count and elapsed_time.
    """
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("bg.mp3")
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    tmx_data = pytmx.util_pygame.load_pygame(level_file)

    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale = min(screen_width / map_width, screen_height / map_height)

    background = pygame.image.load(background_file).convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))

    # Platforms
    platforms = []
    for layer in tmx_data.visible_layers:
        from pytmx import TiledTileLayer
        if isinstance(layer, TiledTileLayer) and getattr(layer, "name", "").lower() == "ground":
            for x, y, gid in layer:
                if gid != 0:
                    rect = pygame.Rect(
                        int(x * tmx_data.tilewidth * scale),
                        int(y * tmx_data.tileheight * scale),
                        int(tmx_data.tilewidth * scale),
                        int(tmx_data.tileheight * scale)
                    )
                    platforms.append(rect)

    # Doors
    door_rects = []
    for layer in tmx_data.visible_layers:
        from pytmx import TiledTileLayer
        if isinstance(layer, TiledTileLayer) and getattr(layer, "name", "").lower() == "door":
            for x, y, gid in layer:
                if gid != 0:
                    rect = pygame.Rect(
                        int(x * tmx_data.tilewidth * scale),
                        int(y * tmx_data.tileheight * scale),
                        int(tmx_data.tilewidth * scale),
                        int(tmx_data.tileheight * scale)
                    )
                    door_rects.append(rect)

    # Player spawn
    spawn_x, spawn_y = 100, 100
    for obj in tmx_data.objects:
        if obj.name and obj.name.lower() == "player":
            spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    # Stones (example)
    stones = pygame.sprite.Group()
    stone_positions = [(200, 200), (400, 300), (600, 150)]
    for pos in stone_positions:
        stones.add(Stone(pos[0], pos[1]))

    moving_platforms = pygame.sprite.Group()
    if "lvl2.tmx" in level_file:   # only show in level 2
        platform = MovingPlatform(300, 400, 100, 20, dx=2, dy=0, move_range=200)
        moving_platforms.add(platform)

    def draw_map(surface):
        for layer in tmx_data.visible_layers:
            from pytmx import TiledTileLayer
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (int(tmx_data.tilewidth * scale), int(tmx_data.tileheight * scale))
                        )
                        surface.blit(tile, (int(x * tmx_data.tilewidth * scale),
                                            int(y * tmx_data.tileheight * scale)))

    # ------------------ Game Loop ------------------
    death_count = 0
    font = pygame.font.Font(None, 50)
    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

        # Death checks
        if player.rect.top > screen_height:
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)
        if pygame.sprite.spritecollide(player, stones, False):
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        # Door collision
        for rect in door_rects:
            if player.rect.colliderect(rect):
                running = False
                break

        # Draw
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        draw_map(screen)
        all_sprites.draw(screen)

        death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
        screen.blit(death_text, (20, 20))
        timer_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 0))
        screen.blit(timer_text, (20, 60))

        pygame.display.flip()
        clock.tick(60)

    for rect in door_rects:
        if player.rect.colliderect(rect): # Save stats
            with open("level_times.txt", "a") as f:
                f.write(f"{level_file}: Time: {elapsed_time:.2f}, Deaths: {death_count}\n")
                f.flush()
                os.fsync(f.fileno())

    pygame.quit()
    return death_count, elapsed_time

# ---------------------- Main Skill Assessment ----------------------
def assess_player():
    print("Starting Level-1 Trial")
    death1, time1 = run_level("lvl1.tmx", "bg1.jpg")

    print("Starting Level-2 Trial")
    death2, time2 = run_level("lvl2.tmx", "bg1.jpg")

    
   

    # Prepare feature vector
    player_features = np.array([[death1, time1, death2, time2]])
    assigned_level = model.predict(player_features)[0]

    print(f"ML Decision: Player should start at Level {assigned_level}")

    # Redirect to chosen level without changing internal logic
    if assigned_level == 1:
        run_level("lvl1.tmx", "bg1.jpg")
    elif assigned_level == 2:
        # Call original lvl2 main function (logic unchanged)
        run_level("lvl2.tmx", "bg1.jpg")
    

# ---------------------- Entry Point ----------------------
if __name__ == "__main__":
    assess_player()