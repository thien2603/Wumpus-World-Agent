import pygame

class Button:
    def __init__(self, rect, text, font, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hover = False

    def draw(self, surface):
        color = (200, 200, 200) if self.hover else (120, 120, 120)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255,255,255), self.rect, width=2, border_radius=8)
        txt_surf = self.font.render(self.text, True, (0,0,0))
        surface.blit(
            txt_surf,
            (self.rect.centerx - txt_surf.get_width() // 2,
             self.rect.centery - txt_surf.get_height() // 2)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()


class Menu:
    def __init__(self, screen, title="Menu", items=None, title_font=None, item_font=None):
        self.screen = screen
        self.title = title
        self.items = items or []  # [(text, callback), ...]
        self.title_font = title_font or pygame.font.Font(None, 72)
        self.item_font = item_font or pygame.font.Font(None, 36)
        self.buttons = []
        self.bg = (10, 10, 30)
        self.result = None
        self.build_buttons()

    def build_buttons(self):
        w, h = self.screen.get_size()
        btn_w, btn_h = w // 3, 50
        start_y = h // 2 - (len(self.items) * (btn_h + 10)) // 2
        self.buttons = []
        for i, (text, cb) in enumerate(self.items):
            rect = (w // 2 - btn_w // 2, start_y + i * (btn_h + 10), btn_w, btn_h)
            btn = Button(rect, text, self.item_font, callback=cb)
            self.buttons.append(btn)

    def draw(self):
        self.screen.fill(self.bg)
        title_surf = self.title_font.render(self.title, True, (255,255,255))
        self.screen.blit(
            title_surf,
            (self.screen.get_width() // 2 - title_surf.get_width() // 2, 80)
        )
        for b in self.buttons:
            b.draw(self.screen)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def run_blocking(self):
        """Hiện menu và chờ user chọn"""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.result = "quit"
                    return self.result
                self.handle_event(event)

            self.build_buttons()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
            if self.result is not None:
                return self.result
