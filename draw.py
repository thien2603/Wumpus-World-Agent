# import pygame
# from agents import SmartAgent
# from world import create_world, move_wumpuses
# from constants import *

# class WorldUI:
#     def __init__(self, screen, world):
#         self.screen = screen
#         self.world = world

#         # View control
#         self.cell_size = BASE_CELL_SIZE
#         self.offset_x = (self.screen.get_width() - len(world) * self.cell_size) // 2
#         self.offset_y = (self.screen.get_height() - len(world) * self.cell_size) // 2

#         # Drag control
#         self.dragging = False
#         self.last_mouse_pos = (0, 0)

#         # Load Agent image if available
#         try:
#             self.agent_img = pygame.image.load("agent.png").convert_alpha()
#         except:
#             self.agent_img = None

#     def zoom(self, factor, mouse_pos=None):
#         old_cell_size = self.cell_size
#         self.cell_size = min(MAX_CELL_SIZE, max(MIN_CELL_SIZE, int(self.cell_size * factor)))

#         if mouse_pos:
#             mouse_grid_x = (mouse_pos[0] - self.offset_x) / old_cell_size
#             mouse_grid_y = (mouse_pos[1] - self.offset_y) / old_cell_size

#             self.offset_x = mouse_pos[0] - mouse_grid_x * self.cell_size
#             self.offset_y = mouse_pos[1] - mouse_grid_y * self.cell_size

#     def reset_view(self):
#         self.cell_size = BASE_CELL_SIZE
#         self.offset_x = (self.screen.get_width() - len(self.world) * self.cell_size) // 2
#         self.offset_y = (self.screen.get_height() - len(self.world) * self.cell_size) // 2

#     def handle_mouse_event(self, event):
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if event.button == 1:   
#                 self.dragging = True
#                 self.last_mouse_pos = event.pos
#             elif event.button == 4: 
#                 self.zoom(1.2, event.pos)
#             elif event.button == 5: 
#                 self.zoom(0.8, event.pos)

#         elif event.type == pygame.MOUSEBUTTONUP:
#             if event.button == 1:   
#                 self.dragging = False

#         elif event.type == pygame.MOUSEMOTION:
#             if self.dragging:  
#                 dx = event.pos[0] - self.last_mouse_pos[0]
#                 dy = event.pos[1] - self.last_mouse_pos[1]
#                 self.offset_x += dx
#                 self.offset_y += dy
#                 self.last_mouse_pos = event.pos

#     def draw_cell(self, x, y, cell):
#         rect = pygame.Rect(
#             self.offset_x + x * self.cell_size,
#             self.offset_y + y * self.cell_size,
#             self.cell_size, self.cell_size
#         )

#         pygame.draw.rect(self.screen, WHITE, rect)
#         pygame.draw.rect(self.screen, GRAY, rect, 1)

#         # Draw cell contents
#         if cell["pit"]:
#             pygame.draw.circle(self.screen, BLACK, rect.center, self.cell_size // 3)
#         elif cell["wumpus"]:
#             pygame.draw.circle(self.screen, RED, rect.center, self.cell_size // 3)
#         elif cell["gold"]:
#             pygame.draw.circle(self.screen, YELLOW, rect.center, self.cell_size // 3)

#         # Percepts as small dots
#         if cell["percept"]["breeze"]:
#             pygame.draw.circle(self.screen, BROWN, (rect.x + 10, rect.y + 10), 5)
#         if cell["percept"]["stench"]:
#             pygame.draw.circle(self.screen, GRAY, (rect.right - 10, rect.y + 10), 5)
#         if cell["percept"]["glitter"]:
#             pygame.draw.circle(self.screen, OLIVE, (rect.centerx, rect.bottom - 10), 5)

#         # Visited cells have a slight tint
#         if cell["visited"]:
#             s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
#             s.fill((200, 200, 255, 50))
#             self.screen.blit(s, rect.topleft)

#     def draw_world(self):
#         Nloc = len(self.world)
#         for y in range(Nloc):
#             for x in range(Nloc):
#                 self.draw_cell(x, y, self.world[y][x])

#     def draw_agent(self, x, y, direction='E'):
#         rect = pygame.Rect(
#             self.offset_x + x * self.cell_size,
#             self.offset_y + y * self.cell_size,
#             self.cell_size, self.cell_size
#         )

#         if self.agent_img:
#             rotation = {'N': 90, 'E': 0, 'S': 270, 'W': 180}[direction]
#             img_rotated = pygame.transform.rotate(self.agent_img, rotation)
#             img_scaled = pygame.transform.smoothscale(img_rotated, (self.cell_size, self.cell_size))
#             self.screen.blit(img_scaled, rect.topleft)
#         else:
#             pygame.draw.circle(self.screen, BLUE, rect.center, self.cell_size // 3)
#             if direction == 'N':
#                 end_pos = (rect.centerx, rect.top + 10)
#             elif direction == 'E':
#                 end_pos = (rect.right - 10, rect.centery)
#             elif direction == 'S':
#                 end_pos = (rect.centerx, rect.bottom - 10)
#             else:  # 'W'
#                 end_pos = (rect.left + 10, rect.centery)
#             pygame.draw.line(self.screen, WHITE, rect.center, end_pos, 2)


# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
#     pygame.display.set_caption("Wumpus")

#     try:
#         programIcon = pygame.image.load("./img/logo_game.jpg")
#         pygame.display.set_icon(programIcon)
#     except:
#         pass

#     world, path = create_world()
#     ui = WorldUI(screen, world)
#     agent = SmartAgent()

#     clock = pygame.time.Clock()
#     running = True
#     auto_play = False
#     show_debug = True

#     font = pygame.font.SysFont('Arial', 16)

#     while running:
#         screen.fill(BROWN)

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_m:
#                     move_wumpuses(world)
#                     agent.on_wumpus_moved(world)
#                 elif event.key == pygame.K_r:
#                     ui.reset_view()
#                 elif event.key == pygame.K_SPACE:
#                     if agent.alive and not agent.found_gold:
#                         agent.act(world)
#                 elif event.key == pygame.K_a:
#                     auto_play = not auto_play
#                 elif event.key == pygame.K_d:
#                     show_debug = not show_debug
#             else:
#                 ui.handle_mouse_event(event)

#         # Auto-play
#         if auto_play and agent.alive and not agent.found_gold:
#             agent.act(world)
#             pygame.time.delay(300)

#         ui.draw_world()
#         ui.draw_agent(agent.x, agent.y, agent.dir)

#         # Status
#         status_text = (
#             f"Score: {agent.score} | Pos: ({agent.x}, {agent.y}) | Dir: {agent.dir} | "
#             f"Gold: {'Yes' if agent.found_gold else 'No'} | "
#             f"Arrow: {'Used' if agent.arrow_used else 'Available'} | "
#             f"Alive: {'Yes' if agent.alive else 'No'}"
#         )
#         screen.blit(font.render(status_text, True, WHITE), (10, 10))

#         controls_text = "Controls: SPACE=Step | A=Auto-play | M=Move Wumpus | R=Reset View | D=Toggle Debug"
#         screen.blit(font.render(controls_text, True, WHITE), (10, 30))

#         if show_debug:
#             debug_lines = [
#                 f"Safe cells: {agent.safe}",
#                 f"Possible pits: {agent.possible_pits}",
#                 f"Possible wumpus: {agent.possible_wumpus}",
#                 f"Visited: {agent.visited}",
#                 f"Dead cells: {agent.dead_cells}"
#             ]
#             for i, line in enumerate(debug_lines):
#                 screen.blit(font.render(line, True, WHITE), (10, 60 + i * 20))

#         pygame.display.flip()
#         clock.tick(60)

#     pygame.quit()


# if __name__ == "__main__":
#     main()
'''
import pygame
from agents import SmartAgent
from world import create_world, move_wumpuses
from constants import *

class WorldUI:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world

        # View control
        self.cell_size = BASE_CELL_SIZE
        self.offset_x = (self.screen.get_width() - len(world) * self.cell_size) // 2
        self.offset_y = (self.screen.get_height() - len(world) * self.cell_size) // 2

        # Drag control
        self.dragging = False
        self.last_mouse_pos = (0, 0)

        # Load images
        def load_img(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except:
                return None

        self.images = {
            "pit": load_img("./img/pit.jpg"),
            "wumpus": load_img("./img/wumpus.jpg"),
            "gold": load_img("./img/gold.jpg"),
            "breeze": load_img("./img/breeze.png"),
            "stench": load_img("./img/stench.jpg"),
            "glitter": load_img("./img/glitter.jpg"),
        }

        # Agent image (sửa lại dùng agent.jpg)
        self.agent_img = load_img("./img/agent.jpg")

    def zoom(self, factor, mouse_pos=None):
        old_cell_size = self.cell_size
        self.cell_size = min(MAX_CELL_SIZE, max(MIN_CELL_SIZE, int(self.cell_size * factor)))

        if mouse_pos:
            mouse_grid_x = (mouse_pos[0] - self.offset_x) / old_cell_size
            mouse_grid_y = (mouse_pos[1] - self.offset_y) / old_cell_size

            self.offset_x = mouse_pos[0] - mouse_grid_x * self.cell_size
            self.offset_y = mouse_pos[1] - mouse_grid_y * self.cell_size

    def reset_view(self):
        self.cell_size = BASE_CELL_SIZE
        self.offset_x = (self.screen.get_width() - len(self.world) * self.cell_size) // 2
        self.offset_y = (self.screen.get_height() - len(self.world) * self.cell_size) // 2

    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:   
                self.dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 4: 
                self.zoom(1.2, event.pos)
            elif event.button == 5: 
                self.zoom(0.8, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:   
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:  
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.offset_x += dx
                self.offset_y += dy
                self.last_mouse_pos = event.pos

    def draw_image_in_cell(self, img, rect, scale_ratio=0.8):
        """Scale image theo cell size và vẽ vào giữa cell"""
        if img:
            size = int(self.cell_size * scale_ratio)
            img_scaled = pygame.transform.smoothscale(img, (size, size))
            img_rect = img_scaled.get_rect(center=rect.center)
            self.screen.blit(img_scaled, img_rect.topleft)

    def draw_cell(self, x, y, cell):
        rect = pygame.Rect(
            self.offset_x + x * self.cell_size,
            self.offset_y + y * self.cell_size,
            self.cell_size, self.cell_size
        )

        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Vẽ nội dung chính
        if cell["pit"]:
            self.draw_image_in_cell(self.images["pit"], rect)
        elif cell["wumpus"]:
            self.draw_image_in_cell(self.images["wumpus"], rect)
        elif cell["gold"]:
            self.draw_image_in_cell(self.images["gold"], rect)

        # Vẽ percept (nhỏ hơn, ở góc)
        if cell["percept"]["breeze"]:
            self.draw_image_in_cell(self.images["breeze"], rect, 0.3)
        if cell["percept"]["stench"]:
            self.draw_image_in_cell(self.images["stench"], rect, 0.3)
        if cell["percept"]["glitter"]:
            self.draw_image_in_cell(self.images["glitter"], rect, 0.3)

        # Visited cells có overlay
        if cell["visited"]:
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            s.fill((200, 200, 255, 50))
            self.screen.blit(s, rect.topleft)

    def draw_world(self):
        Nloc = len(self.world)
        for y in range(Nloc):
            for x in range(Nloc):
                self.draw_cell(x, y, self.world[y][x])

    def draw_agent(self, x, y, direction='E'):
        rect = pygame.Rect(
            self.offset_x + x * self.cell_size,
            self.offset_y + y * self.cell_size,
            self.cell_size, self.cell_size
        )

        if self.agent_img:
            # Xoay ảnh theo hướng
            rotation = {'N': 90, 'E': 0, 'S': 270, 'W': 180}[direction]
            img_rotated = pygame.transform.rotate(self.agent_img, rotation)
            img_scaled = pygame.transform.smoothscale(img_rotated, (self.cell_size, self.cell_size))
            self.screen.blit(img_scaled, rect.topleft)
        else:
            # Nếu không có ảnh thì vẽ circle màu xanh
            pygame.draw.circle(self.screen, BLUE, rect.center, self.cell_size // 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Wumpus")

    try:
        programIcon = pygame.image.load("./img/logo_game.jpg")
        pygame.display.set_icon(programIcon)
    except:
        pass

    world, path = create_world()
    ui = WorldUI(screen, world)
    agent = SmartAgent()

    clock = pygame.time.Clock()
    running = True
    auto_play = False
    show_debug = True

    font = pygame.font.SysFont('Arial', 16)

    while running:
        screen.fill(BROWN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    move_wumpuses(world)
                    agent.on_wumpus_moved(world)
                elif event.key == pygame.K_r:
                    ui.reset_view()
                elif event.key == pygame.K_SPACE:
                    if agent.alive and not agent.found_gold:
                        agent.act(world)
                elif event.key == pygame.K_a:
                    auto_play = not auto_play
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
            else:
                ui.handle_mouse_event(event)

        # Auto-play
        if auto_play and agent.alive and not agent.found_gold:
            agent.act(world)
            pygame.time.delay(300)

        ui.draw_world()
        ui.draw_agent(agent.x, agent.y, agent.dir)

        # Status
        status_text = (
            f"Score: {agent.score} | Pos: ({agent.x}, {agent.y}) | Dir: {agent.dir} | "
            f"Gold: {'Yes' if agent.found_gold else 'No'} | "
            f"Arrow: {'Used' if agent.arrow_used else 'Available'} | "
            f"Alive: {'Yes' if agent.alive else 'No'}"
        )
        screen.blit(font.render(status_text, True, WHITE), (10, 10))

        controls_text = "Controls: SPACE=Step | A=Auto-play | M=Move Wumpus | R=Reset View | D=Toggle Debug"
        screen.blit(font.render(controls_text, True, WHITE), (10, 30))

        if show_debug:
            debug_lines = [
                f"Safe cells: {agent.safe}",
                f"Possible pits: {agent.possible_pits}",
                f"Possible wumpus: {agent.possible_wumpus}",
                f"Visited: {agent.visited}",
                f"Dead cells: {agent.dead_cells}"
            ]
            for i, line in enumerate(debug_lines):
                screen.blit(font.render(line, True, WHITE), (10, 60 + i * 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

'''
import pygame
from agents import SmartAgent
from world import create_world, move_wumpuses
from constants import *

class WorldUI:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world

        # View control
        self.cell_size = BASE_CELL_SIZE
        self.offset_x = (self.screen.get_width() - len(world) * self.cell_size) // 2
        self.offset_y = (self.screen.get_height() - len(world) * self.cell_size) // 2

        # Drag control
        self.dragging = False
        self.last_mouse_pos = (0, 0)

        # Load images
        def load_img(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except:
                return None

        self.images = {
            "pit": load_img("./img/pit.jpg"),
            "wumpus": load_img("./img/wumpus.jpg"),
            "gold": load_img("./img/gold.jpg"),
            "breeze": load_img("./img/breeze.png"),
            "stench": load_img("./img/stench.jpg"),
            "glitter": load_img("./img/glitter.jpg"),
        }

        # Agent image
        self.agent_img = load_img("./img/agent.jpg")

    def zoom(self, factor, mouse_pos=None):
        old_cell_size = self.cell_size
        self.cell_size = min(MAX_CELL_SIZE, max(MIN_CELL_SIZE, int(self.cell_size * factor)))

        if mouse_pos:
            mouse_grid_x = (mouse_pos[0] - self.offset_x) / old_cell_size
            mouse_grid_y = (mouse_pos[1] - self.offset_y) / old_cell_size

            self.offset_x = mouse_pos[0] - mouse_grid_x * self.cell_size
            self.offset_y = mouse_pos[1] - mouse_grid_y * self.cell_size

    def reset_view(self):
        self.cell_size = BASE_CELL_SIZE
        self.offset_x = (self.screen.get_width() - len(self.world) * self.cell_size) // 2
        self.offset_y = (self.screen.get_height() - len(self.world) * self.cell_size) // 2

    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:   
                self.dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 4: 
                self.zoom(1.2, event.pos)
            elif event.button == 5: 
                self.zoom(0.8, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:   
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:  
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.offset_x += dx
                self.offset_y += dy
                self.last_mouse_pos = event.pos

    def draw_image_in_cell(self, img, rect, scale_ratio=0.8):
        """Scale image theo cell size và vẽ vào giữa cell"""
        if img:
            size = int(min(rect.width, rect.height) * scale_ratio)
            img_scaled = pygame.transform.smoothscale(img, (size, size))
            img_rect = img_scaled.get_rect(center=rect.center)
            self.screen.blit(img_scaled, img_rect.topleft)

    def _draw_agent_in_rect(self, rect, direction='E'):
        """Vẽ agent trong rect nhỏ, xoay theo hướng"""
        if self.agent_img:
            rotation = {'N': 90, 'E': 0, 'S': 270, 'W': 180}[direction]
            img_rotated = pygame.transform.rotate(self.agent_img, rotation)
            img_scaled = pygame.transform.smoothscale(img_rotated, (rect.width, rect.height))
            self.screen.blit(img_scaled, rect.topleft)

    def draw_cell(self, x, y, cell, agent_here=None, agent_dir='E'):
        rect = pygame.Rect(
            self.offset_x + x * self.cell_size,
            self.offset_y + y * self.cell_size,
            self.cell_size, self.cell_size
        )

        # Vẽ nền + viền
        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Gom tất cả đối tượng
        imgs = []
        if cell["pit"]:
            imgs.append(self.images["pit"])
        if cell["wumpus"]:
            imgs.append(self.images["wumpus"])
        if cell["gold"]:
            imgs.append(self.images["gold"])
        if cell["percept"]["breeze"]:
            imgs.append(self.images["breeze"])
        if cell["percept"]["stench"]:
            imgs.append(self.images["stench"])
        if cell["percept"]["glitter"]:
            imgs.append(self.images["glitter"])

        # Nếu agent có ở ô này
        if agent_here:
            imgs.append(("agent", agent_dir))

        n = len(imgs)

        if n == 1:
            item = imgs[0]
            if isinstance(item, tuple) and item[0]=="agent":
                self._draw_agent_in_rect(rect, item[1])
            else:
                self.draw_image_in_cell(item, rect, 0.8)
        elif n > 1:
            cols = int(n**0.5 + 0.9999)
            rows = (n + cols - 1) // cols

            sub_w = self.cell_size // cols
            sub_h = self.cell_size // rows

            for i, item in enumerate(imgs):
                row = i // cols
                col = i % cols
                sub_rect = pygame.Rect(
                    rect.x + col * sub_w,
                    rect.y + row * sub_h,
                    sub_w, sub_h
                )
                if isinstance(item, tuple) and item[0]=="agent":
                    self._draw_agent_in_rect(sub_rect, item[1])
                else:
                    self.draw_image_in_cell(item, sub_rect, 0.9)

        # Overlay visited cell
        if cell["visited"]:
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            s.fill((200, 200, 255, 50))
            self.screen.blit(s, rect.topleft)

    def draw_world(self, agent=None):
        Nloc = len(self.world)
        for y in range(Nloc):
            for x in range(Nloc):
                agent_here = (agent.x == x and agent.y == y) if agent else False
                agent_dir = agent.dir if agent_here else 'E'
                self.draw_cell(x, y, self.world[y][x], agent_here, agent_dir)


# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
#     pygame.display.set_caption("Wumpus")

#     try:
#         programIcon = pygame.image.load("./img/logo_game.jpg")
#         pygame.display.set_icon(programIcon)
#     except:
#         pass

#     world, path = create_world()
#     ui = WorldUI(screen, world)
#     agent = SmartAgent()

#     clock = pygame.time.Clock()
#     running = True
#     auto_play = False
#     show_debug = True

#     font = pygame.font.SysFont('Arial', 16)

#     while running:
#         screen.fill(BROWN)

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_m:
#                     move_wumpuses(world)
#                     agent.on_wumpus_moved(world)
#                 elif event.key == pygame.K_r:
#                     ui.reset_view()
#                 elif event.key == pygame.K_SPACE:
#                     if agent.alive and not agent.found_gold:
#                         agent.act(world)
#                 elif event.key == pygame.K_a:
#                     auto_play = not auto_play
#                 elif event.key == pygame.K_d:
#                     show_debug = not show_debug
#             else:
#                 ui.handle_mouse_event(event)

#         # Auto-play
#         if auto_play and agent.alive and not agent.found_gold:
#             agent.act(world)
#             pygame.time.delay(300)

#         ui.draw_world(agent)

#         # Status
#         status_text = (
#             f"Score: {agent.score} | Pos: ({agent.x}, {agent.y}) | Dir: {agent.dir} | "
#             f"Gold: {'Yes' if agent.found_gold else 'No'} | "
#             f"Arrow: {'Used' if agent.arrow_used else 'Available'} | "
#             f"Alive: {'Yes' if agent.alive else 'No'}"
#         )
#         screen.blit(font.render(status_text, True, WHITE), (10, 10))

#         controls_text = "Controls: SPACE=Step | A=Auto-play | M=Move Wumpus | R=Reset View | D=Toggle Debug"
#         screen.blit(font.render(controls_text, True, WHITE), (10, 30))

#         if show_debug:
#             debug_lines = [
#                 f"Safe cells: {agent.safe}",
#                 f"Possible pits: {agent.possible_pits}",
#                 f"Possible wumpus: {agent.possible_wumpus}",
#                 f"Visited: {agent.visited}",
#                 f"Dead cells: {agent.dead_cells}"
#             ]
#             for i, line in enumerate(debug_lines):
#                 screen.blit(font.render(line, True, WHITE), (10, 60 + i * 20))

#         pygame.display.flip()
#         clock.tick(60)

#     pygame.quit()


# if __name__ == "__main__":
#     main()
