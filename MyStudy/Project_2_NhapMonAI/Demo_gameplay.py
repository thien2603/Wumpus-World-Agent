import random
import readchar
# ====== CẤU HÌNH ======
N = 8  # Kích thước bản đồ
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
            if (world[x][y]["gold"]):
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
            if (x, y) != (0, 0) and not world[y][x]["wumpus"]:
                world[y][x]["wumpus"] = True
                wumpus_positions.add((x, y))

        # Đặt Pit
        for y in range(N):
            for x in range(N):
                if (x, y) != (0, 0) and not world[y][x]["wumpus"]:
                    if random.random() < PIT_PROB:
                        world[y][x]["pit"] = True

        # Đặt Gold
        while True:
            x, y = random.randint(0, N-1), random.randint(0, N-1)
            if (x, y) != (0, 0) and not world[y][x]["wumpus"] and not world[y][x]["pit"]:
                world[y][x]["gold"] = True
                break

        # Tính percept
        for y in range(N):
            for x in range(N):
                percept = world[y][x]["percept"]
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < N and 0 <= ny < N:
                        if world[ny][nx]["wumpus"]:
                            percept["stench"] = True
                        if world[ny][nx]["pit"]:
                            percept["breeze"] = True
                if world[y][x]["gold"]:
                    percept["glitter"] = True
        world[1][0]["pit"] = False  # (0,1)
        world[0][1]["pit"] = False  # (1,0)
        path = set()
        if is_reachable(path, world):
            return path, world
        else:
            continue



# ====== AGENT ======
class Agent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dir = 'E'
        self.has_gold = False
        self.alive = True
        self.arrow_used = False

    def turn_left(self):
        idx = DIRECTIONS.index(self.dir)
        self.dir = DIRECTIONS[(idx - 1) % 4]

    def turn_right(self):
        idx = DIRECTIONS.index(self.dir)
        self.dir = DIRECTIONS[(idx + 1) % 4]

    def move_forward(self, world):
        nx = self.x + DX[self.dir]
        ny = self.y + DY[self.dir]
        if 0 <= nx < N and 0 <= ny < N:
            self.x, self.y = nx, ny
            cell = world[self.y][self.x]
            if cell["wumpus"] or cell["pit"]:
                self.alive = False
                print("💀 Agent died!")
        else:
            print("🔁 Bump into wall!")
    def check_current_cell(self, world):
        cell = world[self.y][self.x]
        if cell["gold"]:
            self.has_gold = True
            cell["gold"] = False
            print("✨ Found and automatically grabbed the GOLD!")
    def move(self, dx, dy, world):
        nx = self.x + dx
        ny = self.y + dy
        if 0 <= nx < N and 0 <= ny < N:
            self.x, self.y = nx, ny
            cell = world[self.y][self.x]
            if cell["wumpus"] or cell["pit"]:
                self.alive = False
                print("💀 Agent died!")
        else:
            print("🔁 Bump into wall!")
    def grab(self, world):
        if world[self.y][self.x]["gold"]:
            self.has_gold = True
            world[self.y][self.x]["gold"] = False
            print("✨ Grabbed the gold!")

    def percept(self, world):
        cell = world[self.y][self.x]
        percepts = cell["percept"]
        has_gold = cell["gold"]
        return {"percepts": percepts, "gold": has_gold}
    def shoot(self, dx, dy, world):
        if self.arrow_used:
            print("🚫 Arrow already used!")
            return

        print("🏹 Shooting arrow...")
        self.arrow_used = True
        x, y = self.x, self.y

        while 0 <= x < N and 0 <= y < N:
            x += dx
            y += dy
            if not (0 <= x < N and 0 <= y < N):
                print("🏹 Arrow hit the wall.")
                return
            if world[y][x]["wumpus"]:
                world[y][x]["wumpus"] = False
                print("💀 Wumpus killed! You hear a SCREAM!")
                # Xoá stench ở các ô lân cận
                for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < N and 0 <= ny < N:
                        world[ny][nx]["percept"]["stench"] = False
                return

        print("🏹 Arrow missed.")



# ====== HIỂN THỊ BẢN ĐỒ ======
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
    if agent.has_gold:
        print("💰 Status: Agent HAS the gold!")
    else:
        print("🔍 Status: Agent does NOT have the gold.")
# ====== AGENT HÀNH ĐỘNG ======
# Hàm này sẽ cho phép agent di chuyển và tìm kiếm vàng

def agent_act(world):
    stack = [(0, 0)]  # vị trí hiện tại
    visited = set()
    safe = set([(0, 0)])
    
    while stack:
        x, y = stack.pop()
        visited.add((x, y))
        percept = world[y][x]["percept"]
        
        if percept["glitter"]:
            print("🪙 Found gold!")
            break  # hoặc quay về (0,0)

        if not percept["breeze"] and not percept["stench"]:
            # các ô lân cận an toàn
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in visited:
                    stack.append((nx, ny))
                    safe.add((nx, ny))


# ====== CHẠY MÔ PHỎNG ======
def main():
    path, world = create_world()
    agent = Agent()

    while agent.alive:
        world[agent.y][agent.x]["visited"] = True
        display_world(world, agent, path)

        percept = agent.percept(world)
        print("👀 Percepts:", percept)
        print("🎮 Use arrow keys to move. Press 'g' to grab gold, 'c' to climb, 's' to shoot, 'q' to quit.")
        key = readchar.readkey()
        # Sau khi đọc phím và xử lý hành động
        if key == readchar.key.UP:
            agent.move(0, 1, world)
            agent.check_current_cell(world)
        elif key == readchar.key.DOWN:
            agent.move(0, -1, world)
            agent.check_current_cell(world)
        elif key == readchar.key.LEFT:
            agent.move(-1, 0, world)
            agent.check_current_cell(world)
        elif key == readchar.key.RIGHT:
            agent.move(1, 0, world)
            agent.check_current_cell(world)
        elif key == 's':
            print("🧭 Choose direction to shoot:")
            print("⬆️: w  ⬇️: s  ⬅️: a  ➡️: d")
            shoot_key = readchar.readkey()
            if shoot_key == 'w':
                agent.shoot(0, 1, world)
            elif shoot_key == 's':
                agent.shoot(0, -1, world)
            elif shoot_key == 'a':
                agent.shoot(-1, 0, world)
            elif shoot_key == 'd':
                agent.shoot(1, 0, world)
            else:
                print("❌ Invalid direction for shoot.")

        elif key == 'g':
            agent.grab(world)
        elif key == 'c':
            if agent.x == 0 and agent.y == 0:
                if agent.has_gold:
                    print("🏆 Escaped with gold! You win!")
                else:
                    print("🚪 Escaped without gold.")
                break
            else:
                print("⚠️ You can only climb at (0,0)!")
        elif key == 'q':
            print("👋 Quit game.")
            break
        else:
            print("❌ Invalid key!")

if __name__ == "__main__":
    main()

print("End of simulation.")