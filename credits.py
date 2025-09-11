# credits.py
import pygame
import sys

def show_credits():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Load background image
    bg = pygame.image.load("Credits.png").convert()
    screen_width, screen_height = screen.get_size()
    bg = pygame.transform.scale(bg, (screen_width, screen_height))

    font_title = pygame.font.Font("MedodicaRegular.otf", 120)
    font_small = pygame.font.Font("MedodicaRegular.otf", 50)


    # Back button
    back_btn = pygame.Rect(screen_width - 220, screen_height - 100, 200, 60)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if back_btn.collidepoint(mx, my):
                    running = False  # exit credits

        # Draw background
        screen.blit(bg, (0, 0))

      

        # Draw back button
        pygame.draw.rect(screen, (200, 50, 50), back_btn)
        back_text = font_small.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_btn.x + back_btn.width // 2 - back_text.get_width() // 2,
                                back_btn.y + back_btn.height // 2 - back_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)
