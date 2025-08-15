# world.py
import random
from constants import N, K, PIT_PROB

def is_reachable(path, world):
    visited = [[False for _ in range(N)] for _ in range(N)]
    path.add((0, 0))
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        x, y = stack.pop()
        if (world[y][x]["gold"]):
            return True
        else:
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    if not visited[ny][nx] and not world[ny][nx]["pit"] and not world[ny][nx]["wumpus"]:
                        visited[ny][nx] = True
                        path.add((nx, ny))
                        stack.append((nx, ny))
    return False

def create_world():
    while True:
        world = [[{
            "wumpus": False,
            "pit": False,
            "gold": False,
            "visited": False,
            "percept": {"stench": False, "breeze": False, "glitter": False}
        } for _ in range(N)] for _ in range(N)]

        # place Wumpus
        wumpus_positions = set()
        while len(wumpus_positions) < K:
            x, y = random.randint(0, N-1), random.randint(0, N-1)
            if (x, y) != (0, 0) and (x, y) != (1, 0) and (x, y) != (0, 1) and not world[y][x]["wumpus"]:
                world[y][x]["wumpus"] = True
                wumpus_positions.add((x, y))

        # place pits
        for y in range(N):
            for x in range(N):
                if (x, y) != (0, 0) and not world[y][x]["wumpus"]:
                    if (x, y) != (1, 0) and (x, y) != (0, 1):
                        if random.random() < PIT_PROB:
                            world[y][x]["pit"] = True

        # place gold
        while True:
            x, y = random.randint(0, N-1), random.randint(0, N-1)
            if (x, y) != (0, 0) and not world[y][x]["wumpus"] and not world[y][x]["pit"]:
                world[y][x]["gold"] = True
                break

        # compute percepts
        for y in range(N):
            for x in range(N):
                percept = {"stench": False, "breeze": False, "glitter": False}
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < N and 0 <= ny < N:
                        if world[ny][nx]["wumpus"]:
                            percept["stench"] = True
                        if world[ny][nx]["pit"]:
                            percept["breeze"] = True
                if world[y][x]["gold"]:
                    percept["glitter"] = True
                world[y][x]["percept"] = percept

        path = set()
        if is_reachable(path, world):
            return world, path
        # else repeat

def move_wumpuses(world):
    Nloc = len(world)
    w_positions = [(x, y) for y in range(Nloc) for x in range(Nloc) if world[y][x]["wumpus"]]
    new_positions = set()
    for x, y in w_positions:
        world[y][x]["wumpus"] = False
    for (x, y) in w_positions:
        neighbors = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                if not world[ny][nx]["pit"]:
                    neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
        else:
            nx, ny = x, y
        if (nx, ny) in new_positions:
            alt = [p for p in neighbors if p not in new_positions]
            if alt:
                nx, ny = random.choice(alt)
        world[ny][nx]["wumpus"] = True
        new_positions.add((nx, ny))
    for yy in range(Nloc):
        for xx in range(Nloc):
            world[yy][xx]["percept"]["stench"] = False
    for (wx, wy) in new_positions:
        for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = wx + ddx, wy + ddy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                world[ny][nx]["percept"]["stench"] = True
    return new_positions
