import pygame, pytmx
from player import Player
import lvl2  # your lvl2.py file
from stone import Stone


def run_level1():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("bg.mp3")
    pygame.mixer.music.play(-1)
    
    # --- Screen setup ---
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    # --- Background ---
    background = pygame.image.load("bg1.jpg")
    background = pygame.transform.scale(background, (screen_width, screen_height))
    bg_rect = background.get_rect(center=(screen_width // 2, screen_height // 2))

    # --- Load map ---
    tmx_data = pytmx.util_pygame.load_pygame("lvl1.tmx")

    # Map scale
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale_x = screen_width / map_width
    scale_y = screen_height / map_height
    scale = min(scale_x, scale_y)

    # --- Platforms (Tile Layer "ground") ---
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

    # --- Doors (Object Layer "door") ---
    door_rects = []
    print("Objects in TMX:")
    for obj in tmx_data.objects:
        print(f"Name: {obj.name}, Type: {obj.type}, X: {obj.x}, Y: {obj.y}, W: {obj.width}, H: {obj.height}")
        if obj.name and obj.name.lower() == "door":
            rect = pygame.Rect(
                int(obj.x * scale),
                int(obj.y * scale),
                int(obj.width * scale),
                int(obj.height * scale)
            )
            door_rects.append(rect)

    # --- Draw map ---
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

    # --- Player spawn ---
    spawn_x, spawn_y = 100, 100
    for obj in tmx_data.objects:
        if obj.name and obj.name.lower() == "player":
            spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    # --- Stones ---
    stones = pygame.sprite.Group()
    stone_positions = [(200, 200), (400, 300), (600, 150)]
    for pos in stone_positions:
        stones.add(Stone(pos[0], pos[1]))

    # --- Game Loop ---
    running = True
    switch_to_lvl2 = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)

        # --- Clear + Draw ---
        screen.fill((0, 0, 0))                 # clears old frame
        screen.blit(background, bg_rect)       # background
        draw_map(screen)                       # map
        stones.draw(screen)                    # stones
        all_sprites.draw(screen)               # player

        # --- Draw doors (debug) ---
        for rect in door_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)  # red outline

        pygame.display.flip()
        clock.tick(60)

        # --- Door collision check ---
        for rect in door_rects:
            if player.rect.colliderect(rect):
                print("PLAYER collided with DOOR at:", rect)
                switch_to_lvl2 = True
                running = False
                break

        if switch_to_lvl2:
            lvl2.main()

    pygame.quit()


# Run level1 if this file is executed
if __name__ == "__main__":
    run_level1()