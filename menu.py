import pygame
from tiles import run_level, assess_player
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Puzzle Pulse")

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
TRANSPARENT_HIGHLIGHT = (255, 255, 255, 50)  # White with 50 alpha (transparency)

# Load background image
try:
    background_image = pygame.image.load('menubg.png').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    print("Background image 'Add a heading (1).jpg' not found. Please ensure it's in the same directory.")
    background_image = None

# Menu items and their positions as transparent rectangles
# The height of each rectangle is 20, and their positions have been adjusted.
menu_items = [
    {"action": "enter_game", "rect": pygame.Rect(750, 265, 400, 20)},    # ENTER GAME
    {"action": "settings", "rect": pygame.Rect(750, 340, 400, 20)},      # SETTINGS
    {"action": "credits", "rect": pygame.Rect(750, 389, 400, 20)},       # CREDITS (moved up by 13px)
    {"action": "quit", "rect": pygame.Rect(750, 449, 400, 20)},          # QUIT (moved up by 28px from original)
]

# Function to draw the menu
def draw_menu(mouse_pos):
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        # Fallback if image is not found
        screen.fill((0, 0, 0))

    # Check for hover and draw the transparent highlight
    for item in menu_items:
        if item["rect"].collidepoint(mouse_pos):
            # Create a semi-transparent surface with the same dimensions as the button
            highlight_surface = pygame.Surface((item["rect"].width, item["rect"].height), pygame.SRCALPHA)
            highlight_surface.fill(TRANSPARENT_HIGHLIGHT)
            screen.blit(highlight_surface, item["rect"].topleft)
            
    # Return the clickable areas for event handling
    return {item["action"]: item["rect"] for item in menu_items}

# Main game loop
def start_page():
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        clickable_areas = draw_menu(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check for clicks on menu items
                    for action, rect in clickable_areas.items():
                        if rect.collidepoint(mouse_pos):
                            print(f"Clicked on {action}")
                            # Implement the action based on the click
                            if action == "enter_game":
                                # Placeholder for starting the game
                                print("Starting game...")
                                return "enter_game"
                            elif action == "settings":
                                # Placeholder for settings menu
                                print("Opening settings...")
                                return "settings"
                            elif action == "credits":
                                # Placeholder for credits screen
                                print("Opening credits...")
                                return "credits"
                            elif action == "quit":
                                pygame.quit()
                                sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    action = start_page()
    # You can use the 'action' variable to control the game flow in your main script
    if action == "enter_game":
        # Start the game at Level 1 (or run skill assessment)
        # Option A: Directly load Level 1
        assess_player()

    elif action == "settings":
        # Call your settings function here
        pass
    elif action == "credits":
        # Call your credits function here
        pass
