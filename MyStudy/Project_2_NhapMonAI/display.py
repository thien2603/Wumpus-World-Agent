# display.py
from constants import N

def display_world2(world, agent):
    print("\n=== SMART AGENT VIEW ===")
    for y in reversed(range(N)):
        for x in range(N):
            pos = (x, y)
            cell = world[y][x]
            char = '?'
            if (agent.x, agent.y) == pos:
                char = 'A'
            elif pos in agent.safe:
                char = 'O'
            elif pos in agent.possible_pits or pos in agent.possible_wumpus:
                char = '!'
            elif pos in agent.visited:
                char = '.'
            print(char, end=' ')
        print()
    print(f"Agent at ({agent.x}, {agent.y})  dir={agent.dir}  score={agent.score}")
    if agent.found_gold:
        print("💰 Agent has found the gold!")

def display_world(world, agent, path):
    print("\n=== WORLD MAP ===")
    for y in reversed(range(N)):
        for x in range(N):
            cell = world[y][x]
            char = '?'
            if agent.x == x and agent.y == y:
                char = 'A'
            elif (x, y) in path:
                char = '1'
            elif cell["visited"]:
                char = '.'
            print(char, end=' ')
        print()
    print(f"Agent at ({agent.x}, {agent.y})")
    if getattr(agent, "has_gold", False):
        print("💰 Status: Agent HAS the gold!")
    else:
        print("🔍 Status: Agent does NOT have the gold.")
    for y in reversed(range(N)):
        for x in range(N):
            cell = world[y][x]
            symbol = "."
            if cell["wumpus"]:
                symbol = "W"
            elif cell["pit"]:
                symbol = "P"
            elif cell["gold"]:
                symbol = "G"
            print(symbol, end=" ")
        print()
