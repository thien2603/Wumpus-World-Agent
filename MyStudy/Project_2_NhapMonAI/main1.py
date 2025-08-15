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
        path = set()
        if is_reachable(path, world):
            return world, path
        else:
            continue

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
    print(f"Agent at ({agent.x}, {agent.y})")
    if agent.found_gold:
        print("💰 Agent has found the gold!")


class SmartAgent:
    def __init__(self):
        self.x, self.y = 0, 0
        self.alive = True
        self.found_gold = False
        self.safe = set([(0, 0)])
        self.visited = set()
        self.frontier = [(0, 0)]
        self.possible_pits = set()
        self.possible_wumpus = set()
        self.last_dead_cell = None
        self.dead_cells = set()
        self.id = 0

        # arrow state (để có thể bắn nếu cần)
        self.arrow_used = False

        # ====== Định nghĩa các luật ======
        # belief rules: dùng để cập nhật niềm tin (chạy tất cả mỗi bước)
        self.belief_rules = [
            self.rule_mark_safe_when_no_breeze_no_stench,
            self.rule_mark_possible_pit_when_breeze,
            self.rule_mark_possible_wumpus_when_stench,
            self.rule_cleanup_impossible_candidates,
            self.rule_detect_certain_wumpus  # cố gắng xác định vị trí wumpus nếu có khả năng
        ]

        # decision rules: chạy theo thứ tự, dừng sau khi thực hiện một hành động
        self.decision_rules = [
            self.rule_pick_gold,
            self.rule_move_to_safe_unvisited,
            self.rule_shoot_confirmed_wumpus,
            self.rule_move_least_risk
        ]

    # ----------------- BELIEF RULES -----------------
    def rule_mark_safe_when_no_breeze_no_stench(self, world):
        percepts = world[self.y][self.x]["percept"]
        if not percepts["breeze"] and not percepts["stench"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.dead_cells:
                    self.safe.add((nx, ny))

    def rule_mark_possible_pit_when_breeze(self, world):
        percepts = world[self.y][self.x]["percept"]
        if percepts["breeze"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe:
                    self.possible_pits.add((nx, ny))

    def rule_mark_possible_wumpus_when_stench(self, world):
        percepts = world[self.y][self.x]["percept"]
        if percepts["stench"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe:
                    self.possible_wumpus.add((nx, ny))

    def rule_cleanup_impossible_candidates(self, world):
        # Nếu một ô đã được chứng minh safe => xóa khỏi danh sách nghi ngờ
        self.possible_pits -= self.safe
        self.possible_wumpus -= self.safe
        # Nếu ô đã visited => không còn nghi ngờ
        self.possible_pits -= self.visited
        self.possible_wumpus -= self.visited
        # Tránh các ô đã chết
        self.possible_pits -= self.dead_cells
        self.possible_wumpus -= self.dead_cells
    def get_adjacent(self, x, y):
        """Trả về danh sách các ô kề trong bản đồ."""
        adj = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                adj.append((nx, ny))
        return adj

    def rule_detect_certain_wumpus(self, world):
        # Nếu chỉ còn 1 ô trong possible_wumpus -> coi là "xác định"
        if len(self.possible_wumpus) == 1:
            self.confirmed_wumpus = next(iter(self.possible_wumpus))
        else:
            # cơ bản: nếu một ô nằm trong mọi tập nghi ngờ (sau nhiều stench), có thể xác định,
            # nhưng để đơn giản ta chỉ sử dụng điều kiện len==1
            self.confirmed_wumpus = None

    # ----------------- DECISION RULES -----------------
    def rule_pick_gold(self, world):
        if world[self.y][self.x]["gold"]:
            print(f"🏆 Found GOLD at ({self.x}, {self.y})")
            self.found_gold = True
            # agent không cần set world[...]["gold"]=False ở đây nếu muốn
            return True
        return False

    def rule_move_to_safe_unvisited(self, world):
        safe_unvisited = [c for c in self.safe if c not in self.visited and c not in self.dead_cells]
        if safe_unvisited:
            # chọn ô safe chưa thăm (có thể nâng cấp thành tìm đường gần nhất)
            nx, ny = safe_unvisited[0]
            print(f"➡️ Moving to safe unvisited { (nx, ny) }")
            self.x, self.y = nx, ny
            return True
        return False

    def rule_shoot_confirmed_wumpus(self, world):
        if hasattr(self, "confirmed_wumpus") and self.confirmed_wumpus and not self.arrow_used:
            wx, wy = self.confirmed_wumpus
            dx = 1 if wx > self.x else -1 if wx < self.x else 0
            dy = 1 if wy > self.y else -1 if wy < self.y else 0
            if dx == 0 and dy == 0:
                # nếu confirmed là ô hiện tại (lý thuyết) -> rất xui, tránh
                return False
            print(f"🏹 Shooting arrow towards {self.confirmed_wumpus}")
            self.shoot(dx, dy, world)
            # sau khi bắn, update niềm tin
            self.possible_wumpus.discard(self.confirmed_wumpus)
            self.confirmed_wumpus = None
            return True
        return False

    def rule_move_least_risk(self, world):
        # Tạo tập các ứng viên (possible union). ưu tiên ô ít lần bị nghi ngờ
        candidates = list((self.possible_pits | self.possible_wumpus) - self.visited - self.dead_cells)
        if not candidates:
            return False
        # Score: mỗi nghi ngờ pit = 1, nghi ngờ wumpus = 2 (tăng trọng số)
        def risk_score(cell):
            score = 0
            if cell in self.possible_pits:
                score += 1
            if cell in self.possible_wumpus:
                score += 2
            return score
        candidates.sort(key=lambda c: (risk_score(c), c))  # chọn rủi ro nhỏ nhất
        nx, ny = candidates[0]
        print(f"🤏 Moving into least-risk cell { (nx, ny) } (score={risk_score((nx, ny))})")
        self.x, self.y = nx, ny
        return True

    # ----------------- UTILS: SHOOT -----------------
    def shoot(self, dx, dy, world):
        if self.arrow_used:
            print("🚫 Arrow already used!")
            return
        print("🏹 Arrow launched...")
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
                # Xoá stench ở ô lân cận
                for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < N and 0 <= ny < N:
                        world[ny][nx]["percept"]["stench"] = False
                return
        print("🏹 Arrow missed.")

    # ----------------- APPLY RULES / ACT -----------------
    def apply_belief_rules(self, world):
        # chạy tất cả belief rules (để cập nhật niềm tin)
        for br in self.belief_rules:
            br(world)

    def choose_and_execute_decision(self, world):
        # chạy theo thứ tự decision rules; nếu rule thực hiện hành động -> dừng
        for dr in self.decision_rules:
            performed = dr(world)
            if performed:
                return True
        return False

    def act(self, world):
        # 1) nếu đã tìm vàng -> dừng
        if self.found_gold:
            return

        # 2) mark visited
        self.visited.add((self.x, self.y))
        world[self.y][self.x]["visited"] = True

        # 3) cập nhật niềm tin bằng tập luật
        self.apply_belief_rules(world)

        # 4) in debug
        print("🔎 Beliefs: safe=", self.safe, "possible_pits=", self.possible_pits, "possible_wumpus=", self.possible_wumpus)

        # 5) quyết định hành động theo các luật quyết định
        acted = self.choose_and_execute_decision(world)

        if not acted:
            print("⚠️ No decision rule applied -> agent stuck or no moves available.")

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
        print()  # Xuống dòng sau mỗi hàng
    
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
def main1():
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

def main():
    global N
    N = 4  # Có thể tăng nếu muốn map lớn hơn
    world, path = create_world()  # Bạn cần đảm bảo create_world() return cả path
    agent = SmartAgent()

    print("🌍 Wumpus World created!")
    print("🚀 SmartAgent starting...\n")

    max_steps = 25  # Để tránh lặp vô tận nếu không tìm thấy đường
    steps = 0
    
    while not agent.found_gold and steps < max_steps:
        # Hiển thị map (có thêm ký hiệu đường đi path = '1')
        display_world(world, type('Dummy', (), {
            'x': -1, 'y': -1, 'has_gold': False  # Agent thực tế không cần vẽ ra
        })(), path)

        print(f"\n🔁 Step {steps+1}")
        agent.act(world)
        display_world2(world, agent)
        steps += 1
        if not agent.alive:
            print("♻️ Respawning SmartAgent... avoiding dead cells...\n")
            new_agent = SmartAgent()
            
            # 🔁 Copy lại toàn bộ trạng thái học được
            new_agent.visited = set(agent.visited)
            new_agent.safe = set(agent.safe)
            new_agent.dead_cells = set(agent.dead_cells)
            new_agent.id = agent.id + 1  # Tăng ID để phân biệt agent mới
            # 🔁 Cập nhật lại frontier và nghi ngờ, tránh mọi ô chết
            new_agent.frontier = [cell for cell in agent.frontier if cell not in agent.dead_cells]
            new_agent.possible_pits = set(agent.possible_pits) - agent.dead_cells
            new_agent.possible_wumpus = set(agent.possible_wumpus) - agent.dead_cells

            agent = new_agent
        print("id", agent.id, "front", agent.frontier, "safe", agent.safe, "pits", agent.possible_pits, "wumpus", agent.possible_wumpus, "vísited", agent.visited, "dead", agent.dead_cells)
        print("End of step.\n")

    if agent.found_gold:
        print(f"\n🎉 SmartAgent successfully found the GOLD in {steps} steps!")
    elif not agent.alive:
        print("\n💀 Agent died. Game over.")
    else:
        print("\n❌ Agent failed to find the gold within step limit.")


if __name__ == "__main__":
    main()

print("End of simulation.")