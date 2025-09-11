import pygame, pytmx
from player import Player   # <-- your Player class
pygame.init()

# Fullscreen window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
clock = pygame.time.Clock()

# --- Load Pixel Font ---
# Make sure you have a pixel font TTF file in your project folder (e.g. "pixel_font.ttf")
try:
    font = pygame.font.Font("pixel_font.ttf", 36)  # custom pixelated font
except:
    font = pygame.font.SysFont("Courier", 36, bold=True)  # fallback pixel-style system font

# --- Load map ---
tmx_data = pytmx.util_pygame.load_pygame("lvl2.tmx")

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
    platforms = []
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

                    # Add platform rect for collision
                    platforms.append(pygame.Rect(
                        pos_x, pos_y,
                        int(tmx_data.tilewidth * scale),
                        int(tmx_data.tileheight * scale)
                    ))
    return platforms


# --- Find spawn point in Tiled ---
spawn_x, spawn_y = 100, 100  # default
for obj in tmx_data.objects:
    if obj.name.lower() == "player":
        spawn_x, spawn_y = int(obj.x * scale), int(obj.y * scale)

# Death counter
death_count = 0

# Function to respawn player
def respawn():
    global player, all_sprites, death_count
    death_count += 1
    player = Player(spawn_x, spawn_y)
    all_sprites = pygame.sprite.Group(player)

# Instantiate player
player = Player(spawn_x, spawn_y)
all_sprites = pygame.sprite.Group(player)

# Platforms
platforms = build_platforms(tmx_data, scale)


# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    all_sprites.update(keys, platforms)  # <-- make sure your Player.update accepts (keys, platforms)

    # Respawn condition (example: if player falls below map)
    if player.rect.top > screen_height:
        respawn()

    # --- Draw everything ---
    screen.fill((0, 0, 0))
    draw_map(screen, tmx_data, scale)
    all_sprites.draw(screen)

    # Draw death counter (pixelated)
    death_text = font.render(f"Deaths: {death_count}", True, (255, 0, 0))
    screen.blit(death_text, (20, 20))

    # Debug object check
    for obj in tmx_data.objects:
        if obj.name == "door":
            print("Beans")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
