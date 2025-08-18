# world.py
import random
import constants as C

def is_reachable(path, world):
    """
    Kiểm tra xem có đường đi từ (0,0) tới ô chứa vàng hay không.
    Lấy kích thước từ world (len(world)) thay vì phụ thuộc biến N cứng.
    """
    Nloc = len(world)
    visited = [[False for _ in range(Nloc)] for _ in range(Nloc)]
    path.clear()
    path.add((0, 0))
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        x, y = stack.pop()
        if world[y][x].get("gold", False):
            return True
        else:
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < Nloc and 0 <= ny < Nloc:
                    if not visited[ny][nx] and not world[ny][nx].get("pit", False) and not world[ny][nx].get("wumpus", False):
                        visited[ny][nx] = True
                        path.add((nx, ny))
                        stack.append((nx, ny))
    return False

def create_world(n=None, k=None, pit_prob=None):
    """
    Tạo world mới.
    Tham số (n, k, pit_prob) là tùy chọn — nếu không truyền sẽ dùng constants C.N, C.K, C.PIT_PROB.
    Trả về (world, path) như cũ.
    """
    N = n if n is not None else getattr(C, "N", 8)
    K = k if k is not None else getattr(C, "K", 2)
    PIT = pit_prob if pit_prob is not None else getattr(C, "PIT_PROB", 0.1)

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
                        if random.random() < PIT:
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
        # else repeat and regenerate

def move_wumpuses(world):
    """
    Move each wumpus to a random adjacent cell (not into pits).
    Returns the set of new positions.
    """
    Nloc = len(world)
    # collect current wumpus positions
    w_positions = [(x, y) for y in range(Nloc) for x in range(Nloc) if world[y][x].get("wumpus", False)]

    # shuffle order so movement isn't biased
    random.shuffle(w_positions)

    new_positions = set()

    for (x, y) in w_positions:
        # compute valid neighbor positions (not pits, within bounds)
        neighbors = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                if not world[ny][nx].get("pit", False):
                    neighbors.append((nx, ny))

        # include staying in place as last-resort option
        candidates = neighbors[:]
        not_taken = [p for p in candidates if p not in new_positions]
        if not_taken:
            target = random.choice(not_taken)
        else:
            if (x, y) not in new_positions:
                target = (x, y)
            elif candidates:
                target = random.choice(candidates)
            else:
                target = (x, y)

        new_positions.add(target)

    # clear all old wumpus flags
    for (x, y) in w_positions:
        world[y][x]["wumpus"] = False

    # set new wumpus flags
    for (tx, ty) in new_positions:
        world[ty][tx]["wumpus"] = True

    # recompute stench percepts from scratch (safe for multi-wumpus)
    for yy in range(Nloc):
        for xx in range(Nloc):
            world[yy][xx]["percept"]["stench"] = False

    for (wx, wy) in new_positions:
        for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = wx + ddx, wy + ddy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                world[ny][nx]["percept"]["stench"] = True

    return new_positions
