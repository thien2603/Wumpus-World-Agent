import random
N = 8
K = 2  # Số lượng Wumpus
PIT_PROB = 0.2
def create_world():
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

    return world

def display_world(world):
    for row in world:
        for cell in row:
            if cell["wumpus"]:
                print("W", end=" ")
            elif cell["pit"]:
                print("P", end=" ")
            elif cell["gold"]:
                print("G", end=" ")
            elif cell["percept"]["stench"]:
                print("S", end=" ")
            elif cell["percept"]["breeze"]:
                print("B", end=" ")
            elif cell["percept"]["glitter"]:
                print("L", end=" ")
            else:
                print(".", end=" ")
        print()
    print()
class Agent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dir = 'E'
        self.has_gold = False
        self.alive = True

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

    def turn_left(self):
        directions = ['N', 'W', 'S', 'E']
        idx = directions.index(self.dir)
        self.dir = directions[(idx + 1) % 4]
    def turn_right(self):
        directions = ['N', 'E', 'S', 'W']
        idx = directions.index(self.dir)
        self.dir = directions[(idx + 1) % 4]
    def grab(self, world):
        if world[self.y][self.x]["gold"]:
            self.has_gold = True
            world[self.y][self.x]["gold"] = False
            print("✨ Grabbed the gold!")
    def setAgent(self, world):
        world[0][0]["agent"] = True

def main():
    world = create_world()
    display_world(world)
    agent = Agent()
    agent.setAgent(world)
    agent.alive = True
if __name__ == "__main__":
    main()