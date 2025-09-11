import pygame, pytmx
from player import Player
from stone import Stone
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle
from movingplatform import MovingPlatform
import random


# ---------------------- ML Setup ----------------------
MODEL_FILE = "skill_model.pkl"
LOG_FILE = "level_times.txt"

def base_training():
    """Bootstrap model with some initial training data."""
    X_train = [
        [0, 40, 0, 35],   # very skilled
        [2, 70, 2, 65],   # average
        [6, 120, 6, 115]  # poor
    ]
    y_train = ["Hard", "Medium", "Easy"]

    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(clf, f)

    return clf

def load_or_train_model():
    """Load trained model if available, else create base model."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    else:
        return base_training()

def log_player_data(level, deaths, time_taken):
    """Append player performance stats to log file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{level},{deaths},{int(time_taken)}\n")

def retrain_model():
    """Retrain model using accumulated logs from level_times.txt."""
    if not os.path.exists(LOG_FILE):
        return None

    X, y = [], []
    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            level, deaths, time_taken = parts
            try:
                deaths, time_taken = int(deaths), int(time_taken)
            except ValueError:
                continue

            # Add example
            X.append([deaths, time_taken, deaths, time_taken])
            # Label rule
            if deaths <= 1 and time_taken < 60:
                y.append("Hard")
            elif deaths <= 3 and time_taken < 100:
                y.append("Medium")
            else:
                y.append("Easy")

    if X:
        clf = DecisionTreeClassifier(max_depth=5, random_state=42)
        clf.fit(X, y)
        with open(MODEL_FILE, "wb") as f:
            pickle.dump(clf, f)
        return clf
    return None



# ---------------------- Level Loader ----------------------
def run_level(level_file, background_file, level_num, clf):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("bg.mp3")
    pygame.mixer.music.play(-1)
    scroll_x = 0
    scroll_speed = 1.5
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    tmx_data = pytmx.util_pygame.load_pygame(level_file)
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale = min(screen_width / map_width, screen_height / map_height)

    background = pygame.image.load(background_file).convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))
    bg_width = background.get_width()

    font = pygame.font.Font("MedodicaRegular.otf", 120)
    level_name_text = font.render(f"Level {level_num}", True, (0, 255, 255))

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
    spawn_x, spawn_y = 50, 600
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
        
        moving_platforms.add(mp1)

    

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
    font = pygame.font.Font("MedodicaRegular.otf", 50)
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
        
        scroll_x -= scroll_speed
        if scroll_x <= -bg_width:
            scroll_x = 0
        screen.blit(background, (scroll_x, 0))
        screen.blit(background, (scroll_x + bg_width, 0))

        # Draw
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        draw_map(screen)
        moving_platforms.draw(screen)
        all_sprites.draw(screen)
        screen.blit(level_name_text, (screen_width // 2 - level_name_text.get_width() // 2, 20))


        death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
        timer_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 0))
        screen.blit(death_text, (20, 20))
        screen.blit(timer_text, (20, 60))
        

         # --- Update and draw trail particles ---
        for particle in player.trail_particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.alpha <= 0 or particle.radius <= 0:
                player.trail_particles.remove(particle)

        pygame.display.flip()
        clock.tick(60)

     # Save stats & retrain model
    log_player_data(level_num, death_count, elapsed_time)
    new_clf = retrain_model()
    if new_clf:
        clf = new_clf

    return death_count, elapsed_time, clf

# ---------------------- Skill Assessment ----------------------
def assess_player():
    clf = load_or_train_model()

    print("Starting Level-1 Trial")
    death1, time1, clf = run_level("lvl1.tmx", "bg1.jpg", 1, clf)
    print("Starting Level-2 Trial")
    death2, time2, clf = run_level("lvl2.tmx", "bg1.jpg", 2, clf)

    # ML prediction using trial data
    player_stats = np.array([[death1, time1, death2, time2]])
    predicted_category = clf.predict(player_stats)[0]

    # Map category → level
    category_to_level = {
        "Easy": 1,
        "Medium": 4,
        "Hard": 7
    }
    next_level = category_to_level.get(predicted_category, 3)

    print(f"ML Decision: Player should play category {predicted_category}, starting at Level {next_level}")

    # Level files
    level_files = {i: (f"L{i}.tmx", f"bg1.jpg") for i in range(1, 13)}
    current_level = next_level

    # Loop until end
    while current_level <= 12:
        _, _, clf = run_level(level_files[current_level][0], level_files[current_level][1], current_level, clf)
        current_level += 1
        # Re-check ML prediction after each level
        new_clf = retrain_model()
        if new_clf:
            clf = new_clf
        pred = clf.predict([[0,0,0,0]])[0]  # placeholder, normally use last stats

        #if pred == "Hard":
            #current_level = min(12, current_level + 1)
        #elif pred == "Medium":
            #current_level = min(12, current_level + 2)
        #else:  # Easy
            #current_level = min(12, current_level + 2)


#---- win screen
def victory_screen():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    font_big = pygame.font.Font("MedodicaRegular.otf", 120)
    font_small = pygame.font.Font("MedodicaRegular.otf", 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                raise SystemExit

        screen.fill((0, 0, 0))

        title = font_big.render("Victory!", True, (255, 215, 0))
        msg = font_small.render("Press ESC to exit", True, (255, 255, 255))
       

        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, screen.get_height()//3))
        screen.blit(msg, (screen.get_width()//2 - msg.get_width()//2, screen.get_height()//2))
       

        pygame.display.flip()
        clock.tick(60)


# ---------------------- Entry Point ----------------------
if __name__ == "__main__":
    assess_player()
    print("All levels completed! Showing victory screen...")
    victory_screen()

