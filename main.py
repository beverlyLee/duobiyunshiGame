import pygame
import sys

from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, YELLOW, GRAY
)
from game.core.game import Game
from game.core.audio_manager import SoundType, get_audio_manager
from game.core.skill_tree import load_skill_tree, save_skill_tree, get_skill_tree_manager
from game.ui.skill_tree_ui import SkillTreeUI
from game.ui.button import Button


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("躲避陨石")
    clock = pygame.time.Clock()
    
    skill_tree_manager = load_skill_tree()
    
    game = Game()
    
    skill_tree_ui = SkillTreeUI()
    showing_skill_tree = False
    
    skill_tree_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150,
        200, 50, "技能", YELLOW, (200, 180, 0)
    )
    
    mouse_clicked = False
    
    audio_manager = get_audio_manager()
    audio_manager.load_all_sounds()
    
    last_score_for_points = 0
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_skill_tree(skill_tree_manager)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game.game_over:
                        audio_manager.play_sound(SoundType.BUTTON_CLICK)
                        game.reset()
                elif event.key == pygame.K_p:
                    if game.game_started and not game.game_over:
                        game.paused = not game.paused
                        audio_manager.play_sound(SoundType.BUTTON_CLICK)
                        if game.paused:
                            audio_manager.pause_music()
                        else:
                            audio_manager.resume_music()
                elif event.key == pygame.K_ESCAPE:
                    if showing_skill_tree:
                        showing_skill_tree = False
                        save_skill_tree(skill_tree_manager)
                        audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    elif game.paused:
                        game.paused = False
                        audio_manager.play_sound(SoundType.BUTTON_CLICK)
                        audio_manager.resume_music()
                elif event.key == pygame.K_SPACE:
                    if game.game_started and not game.paused and not game.game_over:
                        game.shoot_bullet()
        
        if showing_skill_tree:
            skill_tree_ui.update()
            
            if mouse_clicked:
                should_close = skill_tree_ui.handle_click(mouse_pos)
                if should_close:
                    showing_skill_tree = False
                    save_skill_tree(skill_tree_manager)
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
            
            skill_tree_ui.draw(screen, mouse_pos)
        else:
            if not game.game_started:
                if game.start_button.is_clicked(mouse_pos, mouse_clicked):
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    last_score_for_points = 0
                    game.reset()
                
                if skill_tree_button.is_clicked(mouse_pos, mouse_clicked):
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    showing_skill_tree = True
            elif game.paused:
                if game.pause_continue_button.is_clicked(mouse_pos, mouse_clicked):
                    game.paused = False
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    audio_manager.resume_music()
                if game.pause_quit_button.is_clicked(mouse_pos, mouse_clicked):
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    save_skill_tree(skill_tree_manager)
                    running = False
            elif game.game_over:
                if game.game_over_restart_button.is_clicked(mouse_pos, mouse_clicked):
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    last_score_for_points = 0
                    game.reset()
                if game.game_over_quit_button.is_clicked(mouse_pos, mouse_clicked):
                    audio_manager.play_sound(SoundType.BUTTON_CLICK)
                    save_skill_tree(skill_tree_manager)
                    running = False
            
            current_score = game.score
            if game.game_started and not game.game_over:
                new_points_from_score = current_score // 1000 - last_score_for_points // 1000
                if new_points_from_score > 0:
                    skill_tree_manager.add_skill_points(new_points_from_score)
                    last_score_for_points = current_score - (current_score % 1000)
                    audio_manager.play_sound(SoundType.POWERUP)
            
            keys = pygame.key.get_pressed()
            game.update(keys)
            game.draw(screen, mouse_pos)
            
            if not game.game_started:
                skill_tree_button.draw(screen, mouse_pos)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    save_skill_tree(skill_tree_manager)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
