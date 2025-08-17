import pygame
from agents import SmartAgent
from world import *
from draw import *

def init_game():
    world, path = create_world()
    agent = SmartAgent()
    return world, agent

def create_ui(screen, world):
    return WorldUI(screen, world)

def show_game_over_screen(screen, result):
    font_large = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 24)
    
    result_text = "You Won!" if result == "win" else "Game Over!"
    restart_text = "Press S to Start New Game | Press X to Exit"
    
    # surface
    overlay = pygame.Surface((400, 150), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (screen.get_width()//2 - 200, screen.get_height()//2 - 75))
    
    result_surf = font_large.render(result_text, True, WHITE)
    restart_surf = font_small.render(restart_text, True, WHITE)
    
    screen.blit(result_surf, (screen.get_width()//2 - result_surf.get_width()//2, 
                            screen.get_height()//2 - 50))
    screen.blit(restart_surf, (screen.get_width()//2 - restart_surf.get_width()//2, 
                             screen.get_height()//2 + 20))

def show_status_bar(screen, agent, show_debug):
    font = pygame.font.SysFont('Arial', 16)
    
    status_text = f"Score: {agent.score} | Pos: ({agent.x},{agent.y}) | Dir: {agent.dir} | " \
                 f"Gold: {'Yes' if agent.found_gold else 'No'} | " \
                 f"Arrow: {'Used' if agent.arrow_used else 'Available'} | " \
                 f"Alive: {'Yes' if agent.alive else 'No'}"
    screen.blit(font.render(status_text, True, WHITE), (10, 10))
    
    # Controls info
    controls_text = "R=Reset View | A=Auto Play | Space=Manual Step | M=Move Wumpus | D=Toggle Debug"
    screen.blit(font.render(controls_text, True, WHITE), (10, 30))

def handle_events(event, world, agent, ui, auto_play, show_debug, game_over):
    if event.type == pygame.QUIT:
        return False, auto_play, show_debug
    
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_m and not game_over:
            move_wumpuses(world)
            agent.on_wumpus_moved(world)
        elif event.key == pygame.K_r:
            ui.reset_view()
        elif event.key == pygame.K_SPACE and not game_over:
            if agent.alive and not agent.found_gold:
                agent.act(world)
        elif event.key == pygame.K_a and not game_over:
            auto_play = not auto_play
        elif event.key == pygame.K_d:
            show_debug = not show_debug
    
    else:
        ui.handle_mouse_event(event)
    
    return True, auto_play, show_debug