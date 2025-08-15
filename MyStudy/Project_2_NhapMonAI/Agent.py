# ====== AGENT (human-controlled) - kept for convenience ======
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
                for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < N and 0 <= ny < N:
                        world[ny][nx]["percept"]["stench"] = False
                return
        print("🏹 Arrow missed.")