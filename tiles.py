import pygame, pytmx
from player import Player
import lvl2  # your lvl2.py file

def run_level1():
    pygame.init()

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

    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

    door_rects = []

    for layer in tmx_data.visible_layers:
        from pytmx import TiledTileLayer
        if isinstance(layer, TiledTileLayer) and getattr(layer, "name", "").lower() == "door":
            for x, y, gid in layer:
                if gid != 0:  # only create rect for non-empty tiles
                    rect = pygame.Rect(
                        int(x * tmx_data.tilewidth * scale),
                        int(y * tmx_data.tileheight * scale),
                        int(tmx_data.tilewidth * scale),
                        int(tmx_data.tileheight * scale)
                    )
                    door_rects.append(rect)





    # --- Game Loop ---
    running = True
    switch_to_lvl2 = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        all_sprites.update(keys, platforms)
        
        for rect in door_rects:
            if player.rect.colliderect(rect):
                print("Collision detected! Switching to Level 2")
                switch_to_lvl2 = True
                running = False  # stop lvl1 loop
                break


        # --- Drawing ---
        screen.fill((0, 0, 0))
        draw_map(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        if switch_to_lvl2:
            lvl2.main()
    

    pygame.quit()

# Run level1 if this file is executed
if __name__ == "__main__":
    run_level1()
