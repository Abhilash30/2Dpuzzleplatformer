import pygame, pytmx
from player import Player
from stone import Stone
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle
from movingplatform import MovingPlatform


# ---------------------- ML Setup ----------------------
X_train = np.array([
    [0, 50, 0, 45],   # very skilled -> Hard
    [1, 60, 1, 55],   # skilled -> Hard
    [2, 70, 2, 65],   # average -> Medium
    [3, 80, 3, 75],   # below average -> Medium
    [4, 90, 4, 85],   # beginner -> Easy
    [5, 100, 5, 95],  # poor performance -> Easy
    [6, 120, 6, 110]  # very poor -> Easy
])

y_train = np.array(["Hard", "Hard", "Medium", "Medium", "Easy", "Easy", "Easy"])

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

with open("skill_model.pkl", "wb") as f:
    pickle.dump(model, f)


# ---------------------- Level Loader ----------------------
def run_level(level_file, background_file):
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
                    rect = pygame.Rect(int(x * tmx_data.tilewidth * scale),
                                       int(y * tmx_data.tileheight * scale),
                                       int(tmx_data.tilewidth * scale),
                                       int(tmx_data.tileheight * scale))
                    platforms.append(rect)

    # Doors
    door_rects = []
    for layer in tmx_data.visible_layers:
        from pytmx import TiledTileLayer
        if isinstance(layer, TiledTileLayer) and getattr(layer, "name", "").lower() == "door":
            for x, y, gid in layer:
                if gid != 0:
                    rect = pygame.Rect(int(x * tmx_data.tilewidth * scale),
                                       int(y * tmx_data.tileheight * scale),
                                       int(tmx_data.tilewidth * scale),
                                       int(tmx_data.tileheight * scale))
                    door_rects.append(rect)

    # Player spawn
    spawn_x, spawn_y = 100, 100
    for obj in tmx_data.objects:
        if obj.name and obj.name.lower() == "player":
            spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)
    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    # Stones
    stones = pygame.sprite.Group()
    stone_positions = [(200, 200), (400, 300), (600, 150)]
    for pos in stone_positions:
        stones.add(Stone(pos[0], pos[1]))

    # Moving Platforms (create ONCE here)
    moving_platforms = pygame.sprite.Group()
    if "L9" in level_file:
        mp1 = MovingPlatform(400, 600, 120, 20, range_x=650, speed=3)  # horizontal
        mp2 = MovingPlatform(600, 450, 120, 20, range_x=200, speed=2)  # vertical
        moving_platforms.add(mp1, mp2)

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
                        surface.blit(tile, (int(x * tmx_data.tilewidth * scale), int(y * tmx_data.tileheight * scale)))

    # ------------------ Game Loop ------------------
    death_count = 0
    font = pygame.font.Font(None, 50)
    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                raise SystemExit
                return death_count, (pygame.time.get_ticks() - start_ticks) / 1000

        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)
        moving_platforms.update()

        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

        # Death checks
        if player.rect.top > screen.get_height():
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        if pygame.sprite.spritecollide(player, stones, False):
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        # Platform collisions
        for platform in moving_platforms:
            if player.rect.colliderect(platform.rect) and player.vel_y >= 0:
                player.rect.bottom = platform.rect.top
                player.vel_y = 0
                # Carry player
                player.rect.x += platform.speed * platform.direction_x
                player.rect.y += platform.speed * platform.direction_y

        # Door collision
        for rect in door_rects:
            if player.rect.colliderect(rect):
                running = False
                break

        # Draw
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        draw_map(screen)
        moving_platforms.draw(screen)
        all_sprites.draw(screen)

        death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
        timer_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 0))
        screen.blit(death_text, (20, 20))
        screen.blit(timer_text, (20, 60))
        pygame.display.flip()
        clock.tick(60)

    # Save stats
    with open("level_times.txt", "a") as f:
        f.write(f"{level_file}: Time: {elapsed_time:.2f}, Deaths: {death_count}\n")
        f.flush()
        os.fsync(f.fileno())

    return death_count, elapsed_time


# ---------------------- Skill Assessment ----------------------
def assess_player():
    print("Starting Level-1 Trial")
    death1, time1 = run_level("lvl1.tmx", "bg1.jpg")
    print("Starting Level-2 Trial")
    death2, time2 = run_level("lvl2.tmx", "bg1.jpg")

    with open("skill_model.pkl", "rb") as f:
        model = pickle.load(f)

    player_stats = np.array([[death1, time1, death2, time2]])
    category = model.predict(player_stats)[0]

    print(f"Initial category (decision tree) -> {category}")

    categories = {
        "Easy": [1, 2, 3, 4],
        "Medium": [5, 6],
        "Hard": [7, 8, 9,10,11,12]
    }

    levels = categories[category]
    current_level_index = 0
    predicted_level = levels[current_level_index]

    level_files = {i: (f"L{i}.tmx", "bg1.jpg") for i in range(1, 13)}

    while predicted_level <= 12:
        print(f"Now playing Level {predicted_level} ({category})")
        death, time = run_level(*level_files[predicted_level])

        if category == "Hard":
            current_level_index += 1
        else:
            if death <= 1 and time < 20:
                if current_level_index + 1 < len(levels):
                    current_level_index += 1
                else:
                    if category == "Easy":
                        category = "Medium"
                        levels = categories["Medium"]
                    elif category == "Medium":
                        category = "Hard"
                        levels = categories["Hard"]
                    current_level_index = 0
            else:
                current_level_index = 0

        if current_level_index >= len(levels):
            break

        predicted_level = levels[current_level_index]


# ---------------------- Entry Point ----------------------
if __name__ == "__main__":
    assess_player()
