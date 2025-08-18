import pygame
import time
from constants import *
from world import create_world, move_wumpuses
from agents import SmartAgent
from draw import *
from menu import Menu   # 👈 import menu

# ================= GLOBAL STATE =================
game_state = {
    "show_debug": True,
    "auto_play": False,
}

# ================= INIT GAME =================
def init_game():
    global N
    N = 4
    world, path = create_world()
    agent = SmartAgent()
    return world, agent

def create_ui(screen, world):
    return WorldUI(screen, world)
# ================= MENU SCREENS =================
def show_main_menu(screen):
    """Main Menu trước khi vào game"""
    def start_cb():
        main_menu.result = "start"
    def options_cb():
        main_menu.result = "options"
    def quit_cb():
        main_menu.result = "quit"

    main_items = [
        ("Start Game", start_cb),
        ("Quit", quit_cb),
    ]
    main_menu = Menu(screen, "Wumpus World", main_items)

    while True:
        res = main_menu.run_blocking()
        if res == "start":
            return "start"
        elif res == "quit":
            return "quit"
        elif res == "options":
            show_options_menu(screen)   # 👈 Gọi 1 lần rồi quay lại menu chính

def show_options_menu(screen):
    """Menu Options để chỉnh debug/auto play"""

    def toggle_debug():
        game_state["show_debug"] = not game_state["show_debug"]

    def toggle_auto():
        game_state["auto_play"] = not game_state["auto_play"]

    def back_cb():
        opt_menu.result = "back"

    opt_items = [
        (f"Show Debug: {'On' if game_state['show_debug'] else 'Off'}", toggle_debug),
        (f"Auto Play: {'On' if game_state['auto_play'] else 'Off'}", toggle_auto),
        ("Back", back_cb),
    ]
    opt_menu = Menu(screen, "Options", opt_items)

    # 👇 chỉ chạy 1 vòng, sau khi chọn Back sẽ return
    res = opt_menu.run_blocking()
    return res

# ================= GAME OVER UI =================
def show_game_over_screen(screen, result):
    font_large = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 24)

    result_text = "You Won!" if result == "win" else "Game Over!"
    restart_text = "Press S to Start New Game | Press X to Exit"

    overlay = pygame.Surface((400, 150), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (screen.get_width()//2 - 200, screen.get_height()//2 - 75))

    result_surf = font_large.render(result_text, True, WHITE)
    restart_surf = font_small.render(restart_text, True, WHITE)

    screen.blit(result_surf, (screen.get_width()//2 - result_surf.get_width()//2,
                            screen.get_height()//2 - 50))
    screen.blit(restart_surf, (screen.get_width()//2 - restart_surf.get_width()//2,
                             screen.get_height()//2 + 20))

# ================= STATUS BAR =================
def show_status_bar(screen, agent, show_debug):
    font = pygame.font.SysFont('Arial', 16)
    status_text = f"Score: {agent.score} | Pos: ({agent.x},{agent.y}) | Dir: {agent.dir} | " \
                 f"Gold: {'Yes' if agent.found_gold else 'No'} | " \
                 f"Arrow: {'Used' if agent.arrow_used else 'Available'} | " \
                 f"Alive: {'Yes' if agent.alive else 'No'}"
    screen.blit(font.render(status_text, True, WHITE), (10, 10))

    controls_text = "R=Reset View | A=Auto Play | Space=Manual Step | M=Move Wumpus | D=Toggle Debug"
    screen.blit(font.render(controls_text, True, WHITE), (10, 30))

# ================= HANDLE EVENTS =================
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

# ================= MAIN LOOP =================
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Wumpus World")

    try:
        programIcon = pygame.image.load("./img/logo_game.jpg")
        pygame.display.set_icon(programIcon)
    except:
        pass

    # === SHOW MAIN MENU ===
    res = show_main_menu(screen)
    if res == "quit":
        pygame.quit()
        return

    # initialize game
    world, agent = init_game()
    ui = create_ui(screen, world)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    auto_play = game_state["auto_play"]
    step = 0
    max_steps = 200

    while running:
        # Game logic
        if not game_over and step < max_steps:
            step += 1
            agent.act(world)
            time.sleep(0.3)

            if step % 5 == 0:
                move_wumpuses(world)
                agent.on_wumpus_moved(world)

            if not agent.alive:
                game_over = True
                result = "lose"
            if agent.found_gold and (agent.x, agent.y) == (0, 0):
                if not (agent.action_history and agent.action_history[-1][0] == "climb_out"):
                    agent.climb_out(world)
                game_over = True
                result = "win"

        # Render
        screen.fill(BLACK)
        ui.draw_world(agent)
        show_status_bar(screen, agent, game_state["show_debug"])

        # Handle events
        for event in pygame.event.get():
            running, auto_play, _ = handle_events(
                event, world, agent, ui, auto_play, game_state["show_debug"], game_over
            )
            if not running:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_s:
                    # Reset game
                    world, agent = init_game()
                    ui = create_ui(screen, world)
                    game_over = False
                    step = 0
                    auto_play = game_state["auto_play"]
                elif event.key == pygame.K_x:
                    running = False
                    pygame.quit()
                    return
                
        # Auto play
        if auto_play and not game_over and agent.alive and not agent.found_gold:
            agent.act(world)
            pygame.time.delay(300)

        if game_over:
            show_game_over_screen(screen, result)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()