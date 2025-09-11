import pygame, pytmx
from player import Player
import os
def main(level1_time=None):   # optional: accept time from lvl1
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("bg.mp3")
    pygame.mixer.music.play(-1)
    with open("level_times.txt", "w") as f:
        f.write("")
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    # Load map
    tmx_data = pytmx.util_pygame.load_pygame("lvl2.tmx")

    # Calculate scale to fit fullscreen
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale = min(screen_width / map_width, screen_height / map_height)

    # --- Find player spawn point ---
    spawn_x, spawn_y = 100, 100
    for obj in tmx_data.objects:
        if obj.name and obj.name.lower() == "player":
            spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    # --- Ground collisions ---
    platforms = []
    from pytmx import TiledTileLayer
    for layer in tmx_data.visible_layers:
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

    # --- Door rects ---
    door_rects = []
    for layer in tmx_data.visible_layers:
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

    # --- Draw map function ---
    def draw_map(surface):
        for layer in tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (int(tmx_data.tilewidth * scale), int(tmx_data.tileheight * scale)))
                        surface.blit(tile, (int(x * tmx_data.tilewidth * scale),
                                            int(y * tmx_data.tileheight * scale)))

    # --- Respawn + Death Counter Setup ---
    death_count = 0
    start_ticks = pygame.time.get_ticks()
    elapsed_time = 0

    # --- Game loop ---
    running = True
    while running:
        font = pygame.font.Font(None, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)

        # Respawn if fall
        if player.rect.top > screen_height:
            death_count += 1
            player.rect.topleft = (spawn_x, spawn_y)

        # Update timer
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

        # --- Check door collision ---
        for rect in door_rects:
            if player.rect.colliderect(rect):
                print(f"PLAYER finished Level 2 in {elapsed_time:.2f} seconds")

                # Save time to file
                with open("level_times.txt", "a") as f:
                    f.write(f"Level2: {elapsed_time:.2f} seconds\n")
                    f.write(f"Level2: {death_count} deaths\n")
                    f.flush()
                    os.fsync(f.fileno())

                running = False
                break

        # --- Drawing ---
        screen.fill((0, 0, 0))
        draw_map(screen)
        all_sprites.draw(screen)

        # HUD
        death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
        screen.blit(death_text, (20, 20))
        timer_text = font.render(f"Time: {elapsed_time:.2f}s", True, (255, 255, 0))
        screen.blit(timer_text, (20, 60))

        # Debug: draw door rects in red
        for rect in door_rects:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
