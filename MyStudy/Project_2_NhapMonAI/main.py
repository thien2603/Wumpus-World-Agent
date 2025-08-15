# main.py
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
