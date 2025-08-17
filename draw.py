
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
            s = pygame.Surface((self.cell_size, self.cell_size))
            s.fill(GRAY)  # Sử dụng màu GRAY đã định nghĩa trong constants
            s.set_alpha(200)  # Độ trong suốt
            self.screen.blit(s, rect.topleft)

    def draw_world(self, agent=None):
        Nloc = len(self.world)
        for y in range(Nloc):
            for x in range(Nloc):
                agent_here = (agent.x == x and agent.y == y) if agent else False
                agent_dir = agent.dir if agent_here else 'E'
                self.draw_cell(x, y, self.world[y][x], agent_here, agent_dir)
