# main.py
'''
from constants import N
from world import create_world, move_wumpuses
from agents import SmartAgent  # and Agent if you want human mode
from display import display_world, display_world2

def main():
    global N
    N = 4  # optionally override for quick tests
    world, path = create_world()
    agent = SmartAgent()
    print("🌍 Wumpus World created!")
    print("🚀 SmartAgent starting...\n")
    max_steps = 200
    steps = 0
    while steps < max_steps:
        steps += 1
        print("\n--- Step", steps, "---")
        display_world(world, type('Dummy', (), {'x': -1, 'y': -1, 'has_gold': False})(), path)
        agent.act(world)
        display_world2(world, agent)
        if steps % 5 == 0:
            print("🕔 5 steps passed -> moving Wumpus(s)...")
            move_wumpuses(world)
            agent.on_wumpus_moved(world)
        if not agent.alive:
            print("\n💀 GAME OVER: SmartAgent died.")
            break
        if agent.found_gold and (agent.x, agent.y) == (0, 0):
            if not (agent.action_history and agent.action_history[-1][0] == "climb_out"):
                agent.climb_out(world)
            print("\n🎉 GAME WON: SmartAgent returned with gold.")
            break
    else:
        print("\n⏳ MAX STEPS reached, stopping simulation.")

    print("\n=== FINAL RESULT ===")
    print("Alive:", agent.alive)
    print("Found gold:", agent.found_gold)
    print("Score:", agent.score)
    print("Steps:", steps)
    print("Last dead cell:", agent.last_dead_cell)
    for rec in agent.action_history[-100:]:
        print(rec)

if __name__ == "__main__":
    main()
'''

import pygame
from constants import *
from world import create_world, move_wumpuses
from agents import SmartAgent
import time
from draw import *
import sys
from support_ui import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Wumpus World")

    try:
        programIcon = pygame.image.load("./img/logo_game.jpg")
        pygame.display.set_icon(programIcon)
    except:
        pass

    # initalize game
    world, agent = init_game()
    ui = create_ui(screen, world)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    auto_play = False
    show_debug = True
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
        show_status_bar(screen, agent, show_debug)

        # Handle event.
        for event in pygame.event.get():
            running, auto_play, show_debug = handle_events(
                event, world, agent, ui, auto_play, show_debug, game_over
            )
            
            # When game over
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_s:
                    # Reset game
                    world, agent = init_game()
                    ui = create_ui(screen, world)
                    game_over = False
                    step = 0
                    auto_play = False
                elif event.key == pygame.K_x:
                    running = False
                    sys.exit()

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