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

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,800),pygame.RESIZABLE)
    pygame.display.set_caption("Wumpus World")

    try:
        programIcon = pygame.image.load("./img/logo_game.jpg")
        pygame.display.set_icon(programIcon)
    except: pass

    global N
    N=4
    world,path=create_world()
    agent=SmartAgent()
    ui=WorldUI(screen,world)

    clock=pygame.time.Clock()
    running=True
    auto_play=False
    show_debug=True

    font=pygame.font.SysFont('Arial',16)
    step=0
    max_steps=200

    while running and step<max_steps:
        step+=1
        agent.act(world)
        time.sleep(0.3)

        if step%5==0:
            move_wumpuses(world)
            agent.on_wumpus_moved(world)

        if not agent.alive:
            running=False 
        if agent.found_gold and (agent.x,agent.y)==(0,0):
            if not (agent.action_history and agent.action_history[-1][0]=="climb_out"):
                agent.climb_out(world)
            running=False

        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_m:
                    move_wumpuses(world)
                    agent.on_wumpus_moved(world)
                elif event.key==pygame.K_r: ui.reset_view()
                elif event.key==pygame.K_SPACE:
                    if agent.alive and not agent.found_gold:
                        agent.act(world)
                elif event.key==pygame.K_a: auto_play=not auto_play
                elif event.key==pygame.K_d: show_debug=not show_debug
            else:
                ui.handle_mouse_event(event)

        if auto_play and agent.alive and not agent.found_gold:
            agent.act(world)
            pygame.time.delay(300)

        ui.draw_world(agent)

        # Status bar
        status_text = f"Score: {agent.score} | Pos: ({agent.x},{agent.y}) | Dir: {agent.dir} | " \
                      f"Gold: {'Yes' if agent.found_gold else 'No'} | " \
                      f"Arrow: {'Used' if agent.arrow_used else 'Available'} | " \
                      f"Alive: {'Yes' if agent.alive else 'No'}"
        screen.blit(font.render(status_text,True,WHITE),(10,10))
        controls_text = "R=Reset View"
        screen.blit(font.render(controls_text,True,WHITE),(10,30))
        
        '''
        if show_debug:
            debug_lines=[
                f"Safe cells: {agent.safe}",
                f"Possible pits: {agent.possible_pits}",
                f"Possible wumpus: {agent.possible_wumpus}",
                f"Visited: {agent.visited}",
                f"Dead cells: {agent.dead_cells}"
            ]
            for i,line in enumerate(debug_lines):
                screen.blit(font.render(line,True,WHITE),(10,60+i*20))

        '''

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    

if __name__=="__main__":
    main()
