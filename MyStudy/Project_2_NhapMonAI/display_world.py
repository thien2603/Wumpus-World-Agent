import SmartAgent
import random
import heapq
import math
from collections import defaultdict

# ====== CẤU HÌNH ======
N = 8  # Kích thước bản đồ (có thể override trong main)
K = 2  # Số lượng Wumpus
PIT_PROB = 0.1

DIRECTIONS = ['N', 'E', 'S', 'W']
DX = {'N': 0, 'E': 1, 'S': 0, 'W': -1}
DY = {'N': 1, 'E': 0, 'S': -1, 'W': 0}

# ====== KIỂM TRA ĐƯỜNG ĐI CÓ THỂ ĐẾN VÀO Ô CÓ VÀNG ======
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

# ====== KHỞI TẠO BẢN ĐỒ ======
def create_world():
    while True:
        world = [[{
            "wumpus": False,
            "pit": False,
            "gold": False,
            "visited": False,
            "percept": {"stench": False, "breeze": False, "glitter": False}
        } for _ in range(N)] for _ in range(N)]

        # Đặt Wumpus
        wumpus_positions = set()
        while len(wumpus_positions) < K:
            x, y = random.randint(0, N-1), random.randint(0, N-1)
            if (x, y) != (0, 0) and (x, y) != (1, 0) and (x, y) != (0, 1) and not world[y][x]["wumpus"]:
                world[y][x]["wumpus"] = True
                wumpus_positions.add((x, y))

        # Đặt Pit
        for y in range(N):
            for x in range(N):
                if (x, y) != (0, 0) and not world[y][x]["wumpus"]:
                    if (x, y) != (1, 0) and (x, y) != (0, 1):  # Đảm bảo không đặt pit ở (0,1) và (1,0)
                        if random.random() < PIT_PROB:
                            world[y][x]["pit"] = True

        # Đặt Gold (ngẫu nhiên)
        while True:
            x, y = random.randint(0, N-1), random.randint(0, N-1)
            if (x, y) != (0, 0) and not world[y][x]["wumpus"] and not world[y][x]["pit"]:
                world[y][x]["gold"] = True
                break

        # Tính percept cho mọi ô
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
        else:
            continue

# ====== HIỂN THỊ SMART AGENT VIEW ======
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

# ============ MOVE WUMPUS FUNCTION =============
def move_wumpuses(world):
    """
    Di chuyển mỗi Wumpus 1 ô sang 1 ô kề ngẫu nhiên (không phải pit).
    Cập nhật lại percept["stench"] cho toàn bộ bản đồ sau khi di chuyển.
    Trả về set vị trí Wumpus mới.
    """
    Nloc = len(world)
    w_positions = [(x, y) for y in range(Nloc) for x in range(Nloc) if world[y][x]["wumpus"]]
    new_positions = set()

    # tạm xóa tất cả wumpus (chúng ta sẽ đặt lại)
    for x, y in w_positions:
        world[y][x]["wumpus"] = False

    for (x, y) in w_positions:
        # tìm các ô kề hợp lệ để di chuyển tới (không phải pit)
        neighbors = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                if not world[ny][nx]["pit"]:
                    neighbors.append((nx, ny))
        # chọn ô ngẫu nhiên nếu có, nếu không thì ở lại
        if neighbors:
            nx, ny = random.choice(neighbors)
        else:
            nx, ny = x, y
        # tránh trùng chọn nếu có thể
        if (nx, ny) in new_positions:
            alt = [p for p in neighbors if p not in new_positions]
            if alt:
                nx, ny = random.choice(alt)
            # else keep (nx,ny) and allow stacking
        world[ny][nx]["wumpus"] = True
        new_positions.add((nx, ny))

    # cập nhật percept stench: xóa tất cả trước, sau đó đặt theo new_positions
    for yy in range(Nloc):
        for xx in range(Nloc):
            world[yy][xx]["percept"]["stench"] = False
    for (wx, wy) in new_positions:
        for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = wx + ddx, wy + ddy
            if 0 <= nx < Nloc and 0 <= ny < Nloc:
                world[ny][nx]["percept"]["stench"] = True

    return new_positions


# ====== HIỂN THỊ BẢN ĐỒ (map & full content) ======
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