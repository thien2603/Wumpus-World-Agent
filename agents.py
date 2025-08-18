import heapq
import math
from collections import defaultdict
from constants import N, DIRECTIONS, DX, DY

class SmartAgent:
    DIRECTIONS = ['N', 'E', 'S', 'W']
    DIR_TO_VEC = {'N': (0,1), 'E': (1,0), 'S': (0,-1), 'W': (-1,0)}

    def __init__(self):
        # basic state
        self.x, self.y = 0, 0
        self.dir = 'E'                 # orientation
        self.alive = True
        self.found_gold = False

        # score
        self.score = 0
        self.action_history = []

        # beliefs / memory
        self.safe = set([(0, 0)])
        self.visited = set()
        self.frontier = [(0, 0)]
        self.possible_pits = set()
        self.possible_wumpus = set()
        self.last_dead_cell = None
        self.id = 0

        # arrow state
        self.arrow_used = False

        # suspicion counts
        self.suspicion_pit_count = defaultdict(int)
        self.suspicion_wumpus_count = defaultdict(int)
        self.MAX_SUSPICION_COUNT = 3

        # cost params
        self.COST_MOVE = 1
        self.COST_TURN = 1
        self.COST_SHOOT = 10
        self.COST_DEATH = 1000

        # belief rules
        self.belief_rules = [
            self.rule_mark_safe_when_no_breeze_no_stench,
            self.rule_mark_possible_pit_when_breeze,
            self.rule_mark_possible_wumpus_when_stench,
            self.rule_cleanup_impossible_candidates,
            self.rule_detect_certain_wumpus
        ]

        # decision rules
        self.decision_rules = [
            self.rule_pick_gold,
            self.rule_return_to_exit_if_has_gold,
            self.rule_move_to_safe_unvisited,
            self.rule_shoot_confirmed_wumpus,
            self.rule_move_least_risk
        ]

    # ----------------- SCORE -----------------
    def update_score(self, action, outcome=None):
        if action == "grab_gold":
            self.score += 10
        elif action in ("move_forward", "move_backward"):
            self.score -= 1
        elif action in ("turn_left", "turn_right"):
            self.score -= 1
        elif action == "shoot":
            self.score -= 10
        elif action == "die":
            self.score -= 1000
        elif action == "climb_out":
            if outcome == "with_gold":
                self.score += 1000
        self.action_history.append((action, outcome, self.score))

    def climb_out(self, world):
        if (self.x, self.y) != (0, 0):
            print("⚠️ Can only climb at (0,0).")
            return
        if self.found_gold:
            print("🏆 Climb out with gold!")
            self.update_score("climb_out", "with_gold")
        else:
            print("🚪 Climb out without gold.")
            self.update_score("climb_out", "without_gold")

    # ----------------- BELIEF RULES -----------------
    def get_adjacent(self, x, y):
        adj = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                adj.append((nx, ny))
        return adj

    def rule_mark_safe_when_no_breeze_no_stench(self, world):
        changed = False
        percepts = world[self.y][self.x]["percept"]
        if not percepts["breeze"] and not percepts["stench"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited:
                    if (nx, ny) not in self.safe:
                        self.safe.add((nx, ny))
                        if (nx, ny) in self.possible_pits:
                            self.possible_pits.discard((nx, ny))
                            if (nx, ny) in self.suspicion_pit_count:
                                del self.suspicion_pit_count[(nx, ny)]
                        if (nx, ny) in self.possible_wumpus:
                            self.possible_wumpus.discard((nx, ny))
                            if (nx, ny) in self.suspicion_wumpus_count:
                                del self.suspicion_wumpus_count[(nx, ny)]
                        changed = True
        return changed

    def rule_mark_possible_pit_when_breeze(self, world):
        changed = False
        percepts = world[self.y][self.x]["percept"]
        if percepts["breeze"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe:
                    if (nx, ny) not in self.possible_pits:
                        self.possible_pits.add((nx, ny))
                        self.suspicion_pit_count[(nx, ny)] += 1
                        changed = True
        return changed

    def rule_mark_possible_wumpus_when_stench(self, world):
        changed = False
        percepts = world[self.y][self.x]["percept"]
        if percepts["stench"]:
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe:
                    if (nx, ny) not in self.possible_wumpus:
                        self.possible_wumpus.add((nx, ny))
                        self.suspicion_wumpus_count[(nx, ny)] += 1
                        changed = True
        return changed

    def rule_cleanup_impossible_candidates(self, world):
        changed = False
        before = set(self.possible_pits)
        self.possible_pits -= self.safe
        self.possible_pits -= self.visited
        if set(self.possible_pits) != before:
            changed = True
        for cell in list(self.suspicion_pit_count.keys()):
            if cell not in self.possible_pits:
                del self.suspicion_pit_count[cell]
        before = set(self.possible_wumpus)
        self.possible_wumpus -= self.safe
        self.possible_wumpus -= self.visited
        if set(self.possible_wumpus) != before:
            changed = True
        for cell in list(self.suspicion_wumpus_count.keys()):
            if cell not in self.possible_wumpus:
                del self.suspicion_wumpus_count[cell]
        return changed

    def rule_detect_certain_wumpus(self, world):
        prev = getattr(self, "confirmed_wumpus", None)
        confirmed = None
        if len(self.possible_wumpus) == 1:
            confirmed = next(iter(self.possible_wumpus))
        else:
            for cell, cnt in self.suspicion_wumpus_count.items():
                if cnt >= self.MAX_SUSPICION_COUNT:
                    confirmed = cell
                    break
        self.confirmed_wumpus = confirmed
        return prev != self.confirmed_wumpus

    # ----------------- FORWARD-CHAINING APPLY -----------------
    def apply_belief_rules(self, world):
        MAX_ITERS = N * N * 10
        iters = 0
        while True:
            iters += 1
            if iters > MAX_ITERS:
                print("⚠️ apply_belief_rules reached MAX_ITERS, stopping.")
                break
            changed_any = False
            for br in self.belief_rules:
                try:
                    changed = br(world)
                except Exception as e:
                    print(f"❌ Exception in belief rule {br.__name__}: {e}")
                    changed = False
                if changed:
                    changed_any = True
            if not changed_any:
                break

    # ----------------- RISK / EXPECTED COST -----------------
    def suspicion_prob_from_count(self, count):
        if count <= 0:
            return 0.0
        return min(1.0, float(count) / float(self.MAX_SUSPICION_COUNT))

    def risk_expected_cost(self, cell):
        p_pit = self.suspicion_prob_from_count(self.suspicion_pit_count.get(cell, 0))
        p_wumpus = self.suspicion_prob_from_count(self.suspicion_wumpus_count.get(cell, 0))
        if not self.arrow_used:
            wumpus_handle_cost = self.COST_SHOOT
        else:
            wumpus_handle_cost = self.COST_DEATH
        expected = p_pit * self.COST_DEATH + p_wumpus * wumpus_handle_cost
        return expected

    # ----------------- A* trên không gian trạng thái (x,y,dir) -----------------
    def turn_left_dir(self, d):
        idx = self.DIRECTIONS.index(d)
        return self.DIRECTIONS[(idx - 1) % 4]

    def turn_right_dir(self, d):
        idx = self.DIRECTIONS.index(d)
        return self.DIRECTIONS[(idx + 1) % 4]

    def heuristic_state(self, pos, goal_pos):
        """
        Heuristic: total expected-risk along the safe path from pos -> goal (sum of risk_expected_cost for each future step).
        If no safe path exists, return 0 (admissible optimistic).
        """
        # accept (x,y) or (x,y,dir)
        if len(pos) == 3:
            sx, sy, sdir = pos
        else:
            sx, sy = pos
            sdir = self.dir

        # if goal isn't in safe, we cannot get a safe-path risk sum -> fallback 0 (admissible)
        if goal_pos != (sx, sy) and goal_pos not in self.safe:
            return 0.0

        path = self._compute_safe_position_path((sx, sy), goal_pos)
        if path is None:
            return 0.0

        # sum only the risk_expected_cost for each step into future cells (do NOT include move/turn costs here)
        total_risk = 0.0
        for i in range(len(path) - 1):
            nx, ny = path[i+1]
            total_risk += self.risk_expected_cost((nx, ny))
        return total_risk

    def _compute_safe_position_path(self, start_pos, goal_pos):
        """
        Compute shortest-cost path (positions only) from start_pos to goal_pos using
        only cells in self.safe (and not in self.dead_cells). Edge cost = COST_MOVE + risk_expected_cost(neighbor).
        Returns list of positions [start,...,goal] or None if no safe path exists.
        """
        sx, sy = start_pos
        gx, gy = goal_pos
        allowed = set(self.safe)
        # allow start even if not in allowed set
        allowed.add((sx, sy))
        if (gx, gy) not in allowed:
            return None

        heap = []
        heapq.heappush(heap, (0.0, (sx, sy)))
        dist = { (sx, sy): 0.0 }
        prev = {}
        while heap:
            cost, cur = heapq.heappop(heap)
            if cur == (gx, gy):
                # reconstruct path
                path = [cur]
                while path[-1] != (sx, sy):
                    path.append(prev[path[-1]])
                path.reverse()
                return path
            if cost > dist.get(cur, math.inf):
                continue
            for nx, ny in self.get_adjacent(cur[0], cur[1]):
                if (nx, ny) not in allowed:
                    continue
                step_cost = self.COST_MOVE + self.risk_expected_cost((nx, ny))
                new_cost = cost + step_cost
                if new_cost < dist.get((nx, ny), math.inf):
                    dist[(nx, ny)] = new_cost
                    prev[(nx, ny)] = cur
                    heapq.heappush(heap, (new_cost, (nx, ny)))
        return None

    def _compute_safe_position_path_cost(self, start_pos, goal_pos):
        """
        Return the total path cost (sum of COST_MOVE + risk_expected_cost for each step)
        along the safest path from start_pos to goal_pos. If no safe path => return math.inf.
        """
        path = self._compute_safe_position_path(start_pos, goal_pos)
        if path is None:
            return math.inf
        total = 0.0
        for i in range(len(path) - 1):
            nx, ny = path[i+1]
            total += self.COST_MOVE + self.risk_expected_cost((nx, ny))
        return total

    # ----------------- NEW: costMove -----------------
    def costMove(self, current_state, neighbor_pos, goal_pos):
        """
        Trả về chi phí 'di chuyển thực tế' khi đi từ current_state -> neighbor_pos **theo yêu cầu**:
        cost = COST_MOVE + safe_path_cost(neighbor_pos -> goal_pos)

        Nếu không tồn tại đường an toàn từ neighbor -> goal, trả về math.inf (bỏ neighbor).
        Lưu ý: turning cost được xử lý bởi các action 'turn_left'/'turn_right' riêng biệt.
        """
        # neighbor_pos is a tuple (nx, ny)
        rem_cost = self._compute_safe_position_path_cost(neighbor_pos, goal_pos)
        if rem_cost == math.inf:
            return math.inf
        return self.COST_MOVE + rem_cost

    def get_neighbors_state(self, state, goal):
        """
        Now accepts `goal`. Returns neighbors with edge cost computed via costMove for forward/back moves.
        """
        x, y, d = state
        neighbors = []
        nd = self.turn_left_dir(d)
        neighbors.append(((x, y, nd), self.COST_TURN, 'turn_left', None))
        nd = self.turn_right_dir(d)
        neighbors.append(((x, y, nd), self.COST_TURN, 'turn_right', None))
        dx, dy = self.DIR_TO_VEC[d]
        nx, ny = x + dx, y + dy
        if 0 <= nx < N and 0 <= ny < N:
            move_cost = self.costMove(state, (nx, ny), goal)
            if move_cost < math.inf:
                neighbors.append(((nx, ny, d), move_cost, 'move_forward', (nx, ny)))
        bdx, bdy = -self.DIR_TO_VEC[d][0], -self.DIR_TO_VEC[d][1]
        bx, by = x + bdx, y + bdy
        if 0 <= bx < N and 0 <= by < N:
            back_cost = self.costMove(state, (bx, by), goal)
            if back_cost < math.inf:
                neighbors.append(((bx, by, d), back_cost, 'move_backward', (bx, by)))
        return neighbors

    def get_path_a_star_state(self, start_state, goal_pos):
        start = start_state
        goal = goal_pos
        open_heap = []
        heapq.heappush(open_heap, (0.0, start))
        came_from = {}
        g_score = {start: 0.0}
        # heuristic is risk_expected_cost-sum along remaining safe path
        f_score = {start: self.heuristic_state(start, goal)}
        closed = set()
        while open_heap:
            _, current = heapq.heappop(open_heap)
            if (current[0], current[1]) == goal:
                path = []
                s = current
                while s in came_from:
                    prev, action_name, action_cost, move_target = came_from[s]
                    path.append((s, action_name, action_cost, move_target))
                    s = prev
                path.append((s, None, 0.0, None))
                path.reverse()
                return path
            if current in closed:
                continue
            closed.add(current)
            for (ns, cost, action_name, move_target) in self.get_neighbors_state(current, goal):
                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(ns, math.inf):
                    came_from[ns] = (current, action_name, cost, move_target)
                    g_score[ns] = tentative_g
                    # h = remaining risk sum
                    h = self.heuristic_state(ns, goal)
                    f = tentative_g + h
                    heapq.heappush(open_heap, (f, ns))
        return None

    # ----------------- DECISION RULES -----------------
    def rule_pick_gold(self, world):
        if world[self.y][self.x]["gold"]:
            print(f"🏆 Found GOLD at ({self.x}, {self.y})")
            self.found_gold = True
            world[self.y][self.x]["gold"] = False
            self.update_score("grab_gold")
            return True
        return False

    def rule_return_to_exit_if_has_gold(self, world):
        if not self.found_gold:
            return False
        if (self.x, self.y) == (0, 0):
            self.climb_out(world)
            return True
        start_state = (self.x, self.y, self.dir)
        path = self.get_path_a_star_state(start_state, (0, 0))
        if path and len(path) >= 2:
            next_state, action_name, _, _ = path[1]
            if action_name == 'turn_left':
                self.dir = next_state[2]
                self.update_score("turn_left")
                print(f"↪️ Turning left -> {self.dir}")
            elif action_name == 'turn_right':
                self.dir = next_state[2]
                self.update_score("turn_right")
                print(f"↪️ Turning right -> {self.dir}")
            elif action_name in ('move_forward', 'move_backward'):
                if action_name == 'move_forward':
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_forward")
                else:
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_backward")
                print(f"➡️ {action_name} to {(self.x, self.y)}")
                cell = world[self.y][self.x]
                if cell["pit"] or cell["wumpus"]:
                    self.alive = False
                    self.last_dead_cell = (self.x, self.y)
                    print("💀 SmartAgent died entering cell!", (self.x, self.y))
                    self.update_score("die")
            return True
        return False

    def rule_shoot_confirmed_wumpus(self, world):
        if hasattr(self, "confirmed_wumpus") and self.confirmed_wumpus and not self.arrow_used:
            wx, wy = self.confirmed_wumpus
            dx = 1 if wx > self.x else -1 if wx < self.x else 0
            dy = 1 if wy > self.y else -1 if wy < self.y else 0
            if dx == 0 and dy == 0:
                return False
            print(f"🏹 Shooting arrow towards {self.confirmed_wumpus}")
            self.shoot(dx, dy, world)
            self.update_score("shoot")
            self.possible_wumpus.discard(self.confirmed_wumpus)
            if self.confirmed_wumpus in self.suspicion_wumpus_count:
                del self.suspicion_wumpus_count[self.confirmed_wumpus]
            self.confirmed_wumpus = None
            return True
        return False

    def rule_move_to_safe_unvisited(self, world):
        safe_unvisited = [c for c in self.safe if c not in self.visited]
        if not safe_unvisited:
            return False
        start_state = (self.x, self.y, self.dir)
        best_path = None
        best_cost = math.inf
        for target in safe_unvisited:
            path = self.get_path_a_star_state(start_state, target)
            if path:
                total = sum(item[2] for item in path if item[1] is not None)
                if total < best_cost:
                    best_cost = total
                    best_path = path
        if best_path and len(best_path) >= 2:
            next_state, action_name, action_cost, move_target = best_path[1]
            if action_name == 'turn_left':
                self.dir = next_state[2]
                self.update_score("turn_left")
                print(f"↪️ Turning left -> now facing {self.dir}")
            elif action_name == 'turn_right':
                self.dir = next_state[2]
                self.update_score("turn_right")
                print(f"↪️ Turning right -> now facing {self.dir}")
            elif action_name in ('move_forward', 'move_backward'):
                if action_name == 'move_forward':
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_forward")
                else:
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_backward")
                print(f"➡️ {action_name} to {(self.x, self.y)}")
                cell = world[self.y][self.x]
                if cell["pit"] or cell["wumpus"]:
                    self.alive = False
                    self.last_dead_cell = (self.x, self.y)
                    print("💀 SmartAgent died entering cell!", (self.x, self.y))
                    self.update_score("die")
            return True
        nx, ny = safe_unvisited[0]
        self.x, self.y = nx, ny
        self.update_score("move_forward")
        print(f"➡️ Fallback direct to {(nx, ny)}")
        return True

    def rule_move_least_risk(self, world):
        candidates = list((self.possible_pits | self.possible_wumpus) - self.visited)
        if not candidates:
            return False
        start_state = (self.x, self.y, self.dir)
        best_choice = None
        best_metric = (math.inf, math.inf)
        best_path = None
        for c in candidates:
            path = self.get_path_a_star_state(start_state, c)
            if path:
                total = sum(item[2] for item in path if item[1] is not None)
                metric = (total, len(path))
            else:
                metric = (self.COST_MOVE + self.risk_expected_cost(c), math.inf)
            if metric < best_metric:
                best_metric = metric
                best_choice = c
                best_path = path
        if best_choice is None:
            return False
        if best_path and len(best_path) >= 2:
            next_state, action_name, action_cost, move_target = best_path[1]
            if action_name == 'turn_left':
                self.dir = next_state[2]
                self.update_score("turn_left")
                print(f"↪️ Turning left -> now facing {self.dir}")
            elif action_name == 'turn_right':
                self.dir = next_state[2]
                self.update_score("turn_right")
                print(f"↪️ Turning right -> now facing {self.dir}")
            elif action_name in ('move_forward', 'move_backward'):
                if action_name == 'move_forward':
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_forward")
                else:
                    self.x, self.y = next_state[0], next_state[1]
                    self.update_score("move_backward")
                print(f"🤏 {action_name} to {(self.x, self.y)} (least-risk)")
                cell = world[self.y][self.x]
                if cell["pit"] or cell["wumpus"]:
                    self.alive = False
                    self.last_dead_cell = (self.x, self.y)
                    print("💀 SmartAgent died entering cell!", (self.x, self.y))
                    self.update_score("die")
            return True
        else:
            nx, ny = best_choice
            self.x, self.y = nx, ny
            self.update_score("move_forward")
            print(f"🤏 Fallback move to least-risk cell {(nx, ny)}")
            return True

    # ----------------- SHOOT -----------------
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
                # kill the wumpus at (x,y)
                world[y][x]["wumpus"] = False
                print("💀 Wumpus killed! You hear a SCREAM!")

                # --- RECOMPUTE ALL 'stench' percepts BASED ON REMAINING WUMPUSes ---
                # First clear all stench
                for yy in range(N):
                    for xx in range(N):
                        world[yy][xx]["percept"]["stench"] = False

                # Then for every remaining wumpus, set stench in adjacent cells
                for yy in range(N):
                    for xx in range(N):
                        if world[yy][xx].get("wumpus", False):
                            for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                                nx, ny = xx + ddx, yy + ddy
                                if 0 <= nx < N and 0 <= ny < N:
                                    world[ny][nx]["percept"]["stench"] = True

                # finished
                return
        print("🏹 Arrow missed.")


    # ----------------- HANDLE WUMPUS MOVE -----------------
    # ----------------- HANDLE WUMPUS MOVE -----------------
    def on_wumpus_moved(self, world):
        """
        Called when Wumpus moved. Rebuild possible_wumpus based on current percepts
        at visited cells and at current position.
        """
        # clear any previous confirmation
        self.confirmed_wumpus = None

        # reset and rebuild
        self.possible_wumpus.clear()
        self.suspicion_wumpus_count.clear()

        # consider visited cells and current cell
        check_cells = set(self.visited)
        check_cells.add((self.x, self.y))
        for (vx, vy) in list(check_cells):
            if not (0 <= vx < N and 0 <= vy < N):
                continue
            percept = world[vy][vx]["percept"]
            if percept.get("stench", False):
                # any adjacent cell to a stench could be a wumpus
                for nx, ny in self.get_adjacent(vx, vy):
                    if (nx, ny) in self.safe:
                        continue
                    # increment suspicion count even if already present
                    self.possible_wumpus.add((nx, ny))
                    self.suspicion_wumpus_count[(nx, ny)] += 1

        # detect certain wumpus if possible
        _ = self.rule_detect_certain_wumpus(world)
        print("🔁 Wumpus moved -> possible_wumpus rebuilt:", self.possible_wumpus,
              "suspicion_counts:", dict(self.suspicion_wumpus_count))


    # ----------------- APPLY RULES / ACT -----------------
    def choose_and_execute_decision(self, world):
        for dr in self.decision_rules:
            performed = dr(world)
            if performed:
                return True
        return False

    def act(self, world):
        """
        Một act() thực hiện đúng 1 action (turn/move/shoot/grab if pick_gold).
        Trước khi quyết định, ta chạy forward-chaining belief rules tới fixed-point.
        Sửa: KHÔNG return sớm khi self.found_gold để rule_return_to_exit_if_has_gold
        có thể lập kế hoạch quay về (0,0) và climb_out.
        """
        # mark visited current cell
        self.visited.add((self.x, self.y))
        world[self.y][self.x]["visited"] = True

        # forward-chain belief rules
        self.apply_belief_rules(world)

        # debug
        print("🔎 Beliefs: safe=", self.safe,
              "possible_pits=", self.possible_pits,
              "possible_wumpus=", self.possible_wumpus,
              "pos=", (self.x, self.y), "dir=", self.dir,
              "suspicion_pit_counts=", dict(self.suspicion_pit_count),
              "suspicion_wumpus_counts=", dict(self.suspicion_wumpus_count),
              "score=", self.score,
              "found_gold=", self.found_gold)

        # make one action decision & execute
        # NOTE: if found_gold == True, rule_return_to_exit_if_has_gold should run first
        acted = self.choose_and_execute_decision(world)
        if not acted:
            # If no decision applied and we have gold, try to climb if at (0,0)
            if self.found_gold and (self.x, self.y) == (0, 0):
                self.climb_out(world)
            else:
                print("⚠️ No decision rule applied -> agent stuck or no moves available.")