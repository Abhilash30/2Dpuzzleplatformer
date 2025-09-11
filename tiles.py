import pygame, pytmx
from player import Player
import lvl2  # your lvl2.py file
from stone import Stone

def run_level1():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("bg.mp3")
    pygame.mixer.music.play(-1)

    # Fullscreen window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    # Load map
    tmx_data = pytmx.util_pygame.load_pygame("lvl1.tmx")

    # Original map size
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    # Scale factor to fit fullscreen
    scale_x = screen_width / map_width
    scale_y = screen_height / map_height
    scale = min(scale_x, scale_y)

    # --- Build platforms from tile layer ---
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

    # --- Find player spawn point ---
    spawn_x, spawn_y = 100, 100
    for obj in tmx_data.objects:
        if obj.name and obj.name.lower() == "player":
            spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

    # Player + sprite groups
    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    # Stones
    stones = pygame.sprite.Group()
    stone_positions = [(200, 200), (400, 300), (600, 150)]
    for pos in stone_positions:
        stones.add(Stone(pos[0], pos[1]))

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

    # --- Respawn + Death Counter Setup ---
    death_count = 0
    font = pygame.font.Font(None, 50)  # default font, can swap with pixel font if you have one

    # --- Game Loop ---
    running = True
    switch_to_lvl2 = False
    start_ticks = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)

        # --- Death check (falls below map or touches stone) ---
        if player.rect.top > screen_height:  # fell out of screen
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        if pygame.sprite.spritecollide(player, stones, False):  # hit stone
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        # --- Door collision check ---
        for rect in door_rects:
            if player.rect.colliderect(rect):
                print("Collision detected! Switching to Level 2")
                switch_to_lvl2 = True
                running = False
                break

        # --- Drawing ---
        screen.fill((0, 0, 0))
        draw_map(screen)
        all_sprites.draw(screen)

        # Draw death counter (top left)
        death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
        screen.blit(death_text, (20, 20))

        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = font.render(f"Time: {seconds}s", True, (255, 255, 0))
        screen.blit(timer_text, (20, 60))

        pygame.display.flip()
        clock.tick(60)
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = font.render(f"Time: {seconds}s", True, (255, 255, 0))
        screen.blit(timer_text, (20, 60))
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = font.render(f"Time: {seconds}s", True, (255, 255, 0))
        screen.blit(timer_text, (20, 60))
        pygame.display.flip()
        clock.tick(60)
       

        if switch_to_lvl2:
            lvl2.main()


    pygame.quit()


if __name__ == "__main__":
    run_level1()