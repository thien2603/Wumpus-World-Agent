# main1.py
import pygame
import time
import copy
from world import create_world, move_wumpuses
from agents import SmartAgent
from Agent import AgentNormal
from draw import *
import constants as C  # import constants module to update N/K
from menu import Menu
import importlib

# ========== GLOBAL UI/FLAGS ==========
game_state = {
    "show_debug": True,
    "auto_play": False,
}

# Use constants N/K as defaults but keep module-level config vars we can change
MAP_N = getattr(C, "N", 8)
MAP_K = getattr(C, "K", 2)



# ----------------- Popup to enter map params (pure pygame) -----------------
def prompt_map_params(screen, default_n=4, default_w=1):
    """
    Modal popup built with pygame to input two integers:
    - N: map size (NxN), int >= 2
    - n_wumpus: number of wumpuses, int >= 0
    Returns (N, n_wumpus) on confirm or None on cancel/close.
    """
    pygame.key.set_repeat(300, 50)
    font = pygame.font.SysFont('Arial', 20)
    title_font = pygame.font.SysFont('Arial', 28, bold=True)

    sw, sh = screen.get_size()
    wbox_w = min(560, int(sw * 0.7))
    wbox_h = 240
    box = pygame.Surface((wbox_w, wbox_h), pygame.SRCALPHA)
    box_rect = box.get_rect(center=(sw // 2, sh // 2))

    # input state
    inputs = [str(default_n), str(default_w)]
    labels = ["Map size N ( 8 >= int >= wumpus + 1)", "Number of Wumpus (int >= 0)"]
    active = 0  # which field is active (0 or 1)

    clock = pygame.time.Clock()
    error_msg = ""

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None
                elif e.key == pygame.K_TAB:
                    active = (active + 1) % 2
                elif e.key == pygame.K_RETURN:
                    # try to parse and validate
                    try:
                        Nval = int(inputs[0])
                        Wval = int(inputs[1])
                        if Nval < 2:
                            error_msg = "N must be >= 2"
                        elif Wval < 0:
                            error_msg = "n_wumpus must be >= 0"
                        elif Wval >= Nval * Nval:
                            error_msg = "Too many wumpuses for map"
                        else:
                            return Nval, Wval
                    except Exception:
                        error_msg = "Please enter valid integers"
                elif e.key == pygame.K_BACKSPACE:
                    if inputs[active]:
                        inputs[active] = inputs[active][:-1]
                else:
                    ch = e.unicode
                    if ch.isdigit():
                        inputs[active] += ch
            elif e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                mx, my = e.pos
                lx = mx - box_rect.x
                ly = my - box_rect.y
                inp_y0 = 70
                inp_h = 36
                gap = 56
                for i in (0, 1):
                    rx = 30
                    ry = inp_y0 + i * gap
                    rw = wbox_w - 60
                    rh = inp_h
                    if 0 <= lx - rx < rw and 0 <= ly - ry < rh:
                        active = i
                        break

        # draw modal
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        box.fill((18, 20, 28, 230))
        title = title_font.render("Map parameters", True, (230, 230, 230))
        box.blit(title, (20, 12))

        # draw labels and inputs
        inp_y0 = 70
        inp_h = 36
        gap = 56
        for i, lbl in enumerate(labels):
            label_surf = font.render(lbl, True, (200, 200, 200))
            box.blit(label_surf, (30, inp_y0 - 24 + i * gap))
            rect = pygame.Rect(30, inp_y0 + i * gap, wbox_w - 60, inp_h)
            pygame.draw.rect(box, (40, 40, 50), rect)
            if i == active:
                pygame.draw.rect(box, (100, 120, 200), rect, 2)
            else:
                pygame.draw.rect(box, (80, 80, 90), rect, 1)
            txt = inputs[i] if inputs[i] != "" else "_"
            txt_surf = font.render(txt, True, (240, 240, 240))
            box.blit(txt_surf, (rect.x + 8, rect.y + 6))

        # error message
        if error_msg:
            err_surf = font.render(error_msg, True, (255, 120, 120))
            box.blit(err_surf, (30, inp_y0 + 2 * gap + 6))

        help_surf = font.render("Enter = OK | Esc = Cancel | Tab = Switch field", True, (150, 150, 150))
        box.blit(help_surf, (30, wbox_h - 34))

        screen.blit(box, box_rect.topleft)
        pygame.display.flip()
        clock.tick(30)


# ----------------- Menu & helpers -----------------
def show_main_menu(screen):
    # declare we will write MAP_N / MAP_K in this function
    global MAP_N, MAP_K

    def start_cb():
        main_menu.result = "start"
    def options_cb():
        main_menu.result = "options"
    def quit_cb():
        main_menu.result = "quit"

    main_items = [
        ("Start Game", start_cb),
        ("Quit", quit_cb),
    ]
    main_menu = Menu(screen, "Wumpus World - Shared Map", main_items)

    while True:
        res = main_menu.run_blocking()
        if res == "start":
            # use MAP_N / MAP_K as defaults (we declared global above)
            params = prompt_map_params(screen, default_n=MAP_N, default_w=MAP_K)
            if params is None:
                continue  # cancelled -> back to menu
            else:
                MAP_N, MAP_K = params
                # --- write changes back into constants module so other modules can read updated values ---
                C.N = MAP_N
                C.K = MAP_K
                C.WINDOW_WIDTH = C.N * C.BASE_CELL_SIZE
                C.WINDOW_HEIGHT = C.N * C.BASE_CELL_SIZE

                # --- QUICK PATCH: cập nhật biến N/K ở các module khác tại runtime ---
                # Thêm tên module bạn muốn patch vào list này nếu cần
                modules_to_update = ["world", "draw", "agents", "Agent", "smart_agent"]
                for mname in modules_to_update:
                    try:
                        m = importlib.import_module(mname)
                    except Exception:
                        continue
                    # set module-level N/K (nếu module có) hoặc tạo thuộc tính
                    try:
                        setattr(m, "N", MAP_N)
                    except Exception:
                        pass
                    try:
                        setattr(m, "K", MAP_K)
                    except Exception:
                        pass
                    # nếu module có set_grid_size, gọi để module internal update
                    try:
                        if hasattr(m, "set_grid_size"):
                            m.set_grid_size(MAP_N)
                    except Exception:
                        pass
                    # update window dims if module uses them
                    try:
                        setattr(m, "WINDOW_WIDTH", MAP_N * C.BASE_CELL_SIZE)
                        setattr(m, "WINDOW_HEIGHT", MAP_N * C.BASE_CELL_SIZE)
                    except Exception:
                        pass

                return "start"
        elif res == "quit":
            return "quit"
        elif res == "options":
            # placeholder: could show options menu
            pass


def show_game_over_screen(surface, result):
    font_large = pygame.font.SysFont('Arial', 36)
    font_small = pygame.font.SysFont('Arial', 18)
    result_text = "You Won!" if result == "win" else "Game Over!"
    restart_text = "Press S to Restart | Press X to Exit"

    sw, sh = surface.get_size()
    w, h = min(480, int(sw * 0.8)), min(140, int(sh * 0.4))
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    overlay_rect = overlay.get_rect(center=(sw // 2, sh // 2))
    surface.blit(overlay, overlay_rect.topleft)

    result_surf = font_large.render(result_text, True, WHITE)
    restart_surf = font_small.render(restart_text, True, WHITE)
    rs = result_surf.get_rect(center=(overlay_rect.centerx, overlay_rect.centery - 20))
    r2 = restart_surf.get_rect(center=(overlay_rect.centerx, overlay_rect.centery + 30))
    surface.blit(result_surf, rs.topleft)
    surface.blit(restart_surf, r2.topleft)


def show_status_bar(surface, agent, show_debug, title=None):
    font = pygame.font.SysFont('Arial', 20)
    if title:
        surface.blit(font.render(title, True, WHITE), (6, 6))
    status_text = f"Score:{agent.score} | Pos:({agent.x},{agent.y}) Dir:{agent.dir} | Gold:{'Yes' if agent.found_gold else 'No'} | Arrow:{'Used' if agent.arrow_used else 'Avail'} | Alive:{'Yes' if agent.alive else 'No'}"
    surface.blit(font.render(status_text, True, WHITE), (6, 24))
    controls_text = "X: Exit | S: Restart | D: Debug"
    surface.blit(font.render(controls_text, True, WHITE), (6, 44))
    if show_debug:
        debug_text = f"Safe:{len(agent.safe)} Visited:{len(agent.visited)} PitC:{len(agent.possible_pits)} WumpC:{len(agent.possible_wumpus)}"
        surface.blit(font.render(debug_text, True, WHITE), (6, 64))


def create_ui_for_surface(surface, world):
    return WorldUI(surface, world)


def reset_shared_game(agent1_cls, agent2_cls):
    """
    Create two world copies (identical layout) and two agents.
    Tries to call create_world(MAP_N, MAP_K) if create_world supports params,
    otherwise falls back to legacy create_world().
    """
    try:
        world1, _ = create_world(MAP_N, MAP_K)
    except TypeError:
        world1, _ = create_world()
    # create an independent copy for the second pane (so changes don't affect the other)
    world2 = copy.deepcopy(world1)
    a1 = agent1_cls()
    a2 = agent2_cls()
    return world1, world2, a1, a2


# ================= MAIN =================
def main():
    pygame.init()

    # initial screen (menu + popup will show here)
    screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Wumpus World - Shared Map (Dual Agents)")

    try:
        programIcon = pygame.image.load("./img/logo_game.jpg")
        pygame.display.set_icon(programIcon)
    except:
        pass

    # show menu (and popup) to possibly update MAP_N / MAP_K
    res = show_main_menu(screen)
    if res == "quit":
        pygame.quit()
        return

    # (optional) if you want to resize window to match chosen MAP_N you could recreate screen here.
    # For now we keep the existing window size.

    # ---- CREATE TWO IDENTICAL WORLDS and two agents ----
    world1, world2, agent1, agent2 = reset_shared_game(SmartAgent, AgentNormal)

    # create initial subsurfaces and UIs
    sw, sh = screen.get_size()
    left_rect = pygame.Rect(0, 0, sw // 2, sh)
    right_rect = pygame.Rect(sw // 2, 0, sw - sw // 2, sh)
    left_surf = screen.subsurface(left_rect)
    right_surf = screen.subsurface(right_rect)

    ui_left = create_ui_for_surface(left_surf, world1)
    ui_right = create_ui_for_surface(right_surf, world2)

    clock = pygame.time.Clock()
    running = True
    game_over1 = False
    game_over2 = False
    result1 = result2 = None

    # --- AUTO: turn both agents ON by default ---
    auto_all = True
    auto1 = True
    auto2 = True

    debug = game_state["show_debug"]

    prev_size = screen.get_size()
    step = 0
    max_steps = 10000

    while running:
        sw, sh = screen.get_size()
        # recreate subsurfaces on resize so UIs recalc offsets
        if (sw, sh) != prev_size:
            left_rect = pygame.Rect(0, 0, sw // 2, sh)
            right_rect = pygame.Rect(sw // 2, 0, sw - sw // 2, sh)
            left_surf = screen.subsurface(left_rect)
            right_surf = screen.subsurface(right_rect)
            ui_left = create_ui_for_surface(left_surf, world1)
            ui_right = create_ui_for_surface(right_surf, world2)
            prev_size = (sw, sh)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    running = False
                    break
                elif event.key == pygame.K_d:
                    debug = not debug
                    game_state["show_debug"] = debug
                elif event.key == pygame.K_s:
                    # restart both worlds and agents (keep auto ON)
                    world1, world2, agent1, agent2 = reset_shared_game(SmartAgent, AgentNormal)
                    ui_left = create_ui_for_surface(left_surf, world1)
                    ui_right = create_ui_for_surface(right_surf, world2)
                    game_over1 = game_over2 = False
                    result1 = result2 = None
                    auto_all = True
                    auto1 = True
                    auto2 = True
                    step = 0

            # mouse events: translate positions into local subsurface coordinates
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                mx, my = event.pos
                # left surface
                if 0 <= mx < sw // 2:
                    local = (mx - left_rect.x, my - left_rect.y)
                    new_event = pygame.event.Event(event.type, {**event.dict, "pos": local})
                    ui_left.handle_mouse_event(new_event)
                else:
                    # right surface
                    local = (mx - right_rect.x, my - right_rect.y)
                    new_event = pygame.event.Event(event.type, {**event.dict, "pos": local})
                    ui_right.handle_mouse_event(new_event)

        # automatic acting
        if not game_over1 and auto1 and agent1.alive:
            agent1.act(world1)
            pygame.time.delay(80)
        if not game_over2 and auto2 and agent2.alive:
            agent2.act(world2)
            pygame.time.delay(80)
        if auto1 and step % 5 == 0:
            if not game_over1:
                newpos = move_wumpuses(world1)
                agent1.on_wumpus_moved(world1)
        if auto2 and step % 5 == 0:
            if not game_over2:
                newpos = move_wumpuses(world1)
                agent2.on_wumpus_moved(world2)

        # post-act checks (per-agent, per-world)
        if agent1.found_gold and (agent1.x, agent1.y) == (0, 0):
            if not (agent1.action_history and agent1.action_history[-1][0] == "climb_out"):
                agent1.climb_out(world1)
            game_over1 = True
            result1 = "win"
        if not agent1.alive:
            game_over1 = True
            result1 = "lose"

        if agent2.found_gold and (agent2.x, agent2.y) == (0, 0):
            if not (agent2.action_history and agent2.action_history[-1][0] == "climb_out"):
                agent2.climb_out(world2)
            game_over2 = True
            result2 = "win"
        if not agent2.alive:
            game_over2 = True
            result2 = "lose"

        # Render
        screen.fill(BLACK)

        # left view: draw world1 and agent1
        left_surf.fill((20, 20, 30))
        ui_left.screen = left_surf
        ui_left.world = world1
        ui_left.draw_world(agent1)
        show_status_bar(left_surf, agent1, debug, title="SmartAgent (Left)")
        if game_over1:
            show_game_over_screen(left_surf, result1)

        # right view: draw world2 and agent2
        right_surf.fill((18, 18, 28))
        ui_right.screen = right_surf
        ui_right.world = world2
        ui_right.draw_world(agent2)
        show_status_bar(right_surf, agent2, debug, title="AgentNormal (Right)")
        if game_over2:
            show_game_over_screen(right_surf, result2)

        # vertical divider
        pygame.draw.line(screen, GRAY, (sw // 2, 0), (sw // 2, sh), 2)

        pygame.display.flip()
        clock.tick(60)
        step += 1
        if step > max_steps:
            auto1 = auto2 = auto_all = False

    pygame.quit()


if __name__ == "__main__":
    main()
