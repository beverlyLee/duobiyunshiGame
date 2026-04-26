import pygame
import sys

from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK
)
from game.core.game import Game

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("躲避陨石")
    clock = pygame.time.Clock()
    
    game = Game()
    
    mouse_clicked = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game.game_over:
                        game.reset()
                elif event.key == pygame.K_p:
                    if game.game_started and not game.game_over:
                        game.paused = not game.paused
                elif event.key == pygame.K_ESCAPE:
                    if game.paused:
                        game.paused = False
                elif event.key == pygame.K_SPACE:
                    if game.game_started and not game.paused and not game.game_over:
                        game.shoot_bullet()
        
        if not game.game_started:
            if game.start_button.is_clicked(mouse_pos, mouse_clicked):
                game.reset()
        elif game.paused:
            if game.pause_continue_button.is_clicked(mouse_pos, mouse_clicked):
                game.paused = False
            if game.pause_quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False
        elif game.game_over:
            if game.game_over_restart_button.is_clicked(mouse_pos, mouse_clicked):
                game.reset()
            if game.game_over_quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False
        
        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(screen, mouse_pos)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
