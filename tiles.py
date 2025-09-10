import pygame, pytmx
from player import Player   # <-- your Player class
import lvl2  # your lvl2.py file

pygame.init()

# Fullscreen window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
clock = pygame.time.Clock()

# --- Load map ---
tmx_data = pytmx.util_pygame.load_pygame("lvl1.tmx")

# Original map size
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight

# Scale factor to fit fullscreen
scale_x = screen_width / map_width
scale_y = screen_height / map_height
scale = min(scale_x, scale_y)  # keep aspect ratio

# --- Build platforms from tile layer ---
def build_platforms(tmx_data, scale):
    platforms = []
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            if layer.name.lower() == "ground":   # only collide with ground layer
                for x, y, gid in layer:
                    if gid != 0:
                        rect = pygame.Rect(
                            int(x * tmx_data.tilewidth * scale),
                            int(y * tmx_data.tileheight * scale),
                            int(tmx_data.tilewidth * scale),
                            int(tmx_data.tileheight * scale),
                        )
                        platforms.append(rect)
    return platforms

# --- Draw map ---
def draw_map(surface, tmx_data, scale):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Resize tile
                    tile = pygame.transform.scale(
                        tile,
                        (int(tmx_data.tilewidth * scale), int(tmx_data.tileheight * scale))
                    )
                    pos_x = int(x * tmx_data.tilewidth * scale)
                    pos_y = int(y * tmx_data.tileheight * scale)
                    surface.blit(tile, (pos_x, pos_y))


# --- Find spawn point in Tiled ---
spawn_x, spawn_y = 100, 100  # default
for obj in tmx_data.objects:
    if obj.name.lower() == "player":
        spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

# Instantiate player
player = Player(spawn_x, spawn_y)
all_sprites = pygame.sprite.Group(player)

# Platforms
platforms = build_platforms(tmx_data, scale)


door_rect = None
for obj in tmx_data.objects:
    if obj.name and obj.name.lower() == "door":
        door_rect = pygame.Rect(
            int(obj.x * scale),
            int(obj.y * scale),
            int(obj.width * scale),
            int(obj.height * scale)
        )
print("Final Door rect:", door_rect)
# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    all_sprites.update(keys, platforms)

    
    # --- Check door collision ---
    if door_rect and player.rect.colliderect(door_rect):
        print("AGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
        print("COLLISION DETECTED -> Switching to Level 2")
        running = False   # stop lvl1 loop
        pygame.quit()     # quit this pygame instance
        import lvl2
        lvl2.main()

    # --- Drawing ---
    screen.fill((0, 0, 0))
    draw_map(screen, tmx_data, scale)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()