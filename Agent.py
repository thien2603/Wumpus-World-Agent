# agentnormal.py
import math
from collections import defaultdict
from constants import N

class AgentNormal:
    DIRECTIONS = ['N', 'E', 'S', 'W']
    DIR_TO_VEC = {'N': (0,1), 'E': (1,0), 'S': (0,-1), 'W': (-1,0)}

    def __init__(self):
        # basic state
        self.x, self.y = 0, 0
        self.dir = 'E'
        self.alive = True
        self.found_gold = False

        # score & history
        self.score = 0
        self.action_history = []

        # beliefs / memory
        self.safe = set([(0, 0)])
        self.visited = set()
        self.frontier = [(0, 0)]
        self.possible_pits = set()
        self.possible_wumpus = set()
        self.last_dead_cell = None
        self.dead_cells = set()
        self.id = 0

        # arrow
        self.arrow_used = False

        # suspicion counters
        self.suspicion_pit_count = defaultdict(int)
        self.suspicion_wumpus_count = defaultdict(int)
        self.MAX_SUSPICION_COUNT = 3

        # costs / params (used for heuristics only)
        self.COST_MOVE = 1
        self.COST_TURN = 1
        self.COST_SHOOT = 10
        self.COST_DEATH = 1000

        # belief rules (same spirit as SmartAgent)
        self.belief_rules = [
            self.rule_mark_safe_when_no_breeze_no_stench,
            self.rule_mark_possible_pit_when_breeze,
            self.rule_mark_possible_wumpus_when_stench,
            self.rule_cleanup_impossible_candidates,
            self.rule_detect_certain_wumpus
        ]

        # decision rules (ordered)
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
            # can't climb unless at (0,0)
            return
        if self.found_gold:
            self.update_score("climb_out", "with_gold")
        else:
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
        if not percepts.get("breeze", False) and not percepts.get("stench", False):
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.dead_cells:
                    if (nx, ny) not in self.safe:
                        self.safe.add((nx, ny))
                        # remove from possible lists if present
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
        if percepts.get("breeze", False):
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe and (nx, ny) not in self.dead_cells:
                    if (nx, ny) not in self.possible_pits:
                        self.possible_pits.add((nx, ny))
                        self.suspicion_pit_count[(nx, ny)] += 1
                        changed = True
        return changed

    def rule_mark_possible_wumpus_when_stench(self, world):
        changed = False
        percepts = world[self.y][self.x]["percept"]
        if percepts.get("stench", False):
            for nx, ny in self.get_adjacent(self.x, self.y):
                if (nx, ny) not in self.visited and (nx, ny) not in self.safe and (nx, ny) not in self.dead_cells:
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
        self.possible_pits -= self.dead_cells
        if set(self.possible_pits) != before:
            changed = True
        for cell in list(self.suspicion_pit_count.keys()):
            if cell not in self.possible_pits:
                del self.suspicion_pit_count[cell]

        before = set(self.possible_wumpus)
        self.possible_wumpus -= self.safe
        self.possible_wumpus -= self.visited
        self.possible_wumpus -= self.dead_cells
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

    def apply_belief_rules(self, world):
        MAX_ITERS = N * N * 10
        iters = 0
        while True:
            iters += 1
            if iters > MAX_ITERS:
                break
            changed_any = False
            for br in self.belief_rules:
                try:
                    changed = br(world)
                except Exception:
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

    # ----------------- simple local movement helpers -----------------
    def turn_left_dir(self, d):
        idx = self.DIRECTIONS.index(d)
        return self.DIRECTIONS[(idx - 1) % 4]

    def turn_right_dir(self, d):
        idx = self.DIRECTIONS.index(d)
        return self.DIRECTIONS[(idx + 1) % 4]

    def _rotate_towards(self, desired_dir):
        """Rotate one step towards desired_dir (choose left or right minimal)"""
        if self.dir == desired_dir:
            return False
        curr_idx = self.DIRECTIONS.index(self.dir)
        desired_idx = self.DIRECTIONS.index(desired_dir)
        diff = (desired_idx - curr_idx) % 4
        # diff: 1 => right, 3 => left, 2 => either (choose right)
        if diff == 1:
            self.dir = self.turn_right_dir(self.dir)
            self.update_score("turn_right")
            return True
        elif diff == 3:
            self.dir = self.turn_left_dir(self.dir)
            self.update_score("turn_left")
            return True
        else:  # diff == 2
            # do a right turn (two turns will follow on subsequent calls)
            self.dir = self.turn_right_dir(self.dir)
            self.update_score("turn_right")
            return True

    def _move_forward_if_facing(self, world):
        """Move forward one cell if within bounds and not a known dead cell. Returns True if moved."""
        dx, dy = self.DIR_TO_VEC[self.dir]
        nx, ny = self.x + dx, self.y + dy
        if not (0 <= nx < N and 0 <= ny < N):
            return False
        if (nx, ny) in self.dead_cells:
            return False
        # perform move
        self.x, self.y = nx, ny
        self.update_score("move_forward")
        # check death
        cell = world[self.y][self.x]
        if cell.get("pit", False) or cell.get("wumpus", False):
            self.alive = False
            self.dead_cells.add((self.x, self.y))
            self.last_dead_cell = (self.x, self.y)
            self.update_score("die")
        return True

    def move_towards(self, target, world):
        """
        Greedy single-step move towards target:
        - Compute primary axis (x or y) to reduce Manhattan distance.
        - Rotate toward that direction if not facing, else move forward.
        - Returns True if an action (turn or move) executed.
        """
        tx, ty = target
        if (self.x, self.y) == (tx, ty):
            return False

        # decide desired direction along axis with larger distance
        dx = tx - self.x
        dy = ty - self.y
        # prefer horizontal if abs(dx) >= abs(dy), else vertical
        if abs(dx) >= abs(dy):
            desired = 'E' if dx > 0 else 'W'
            if dx == 0:  # fallback to vertical if no horizontal delta
                desired = 'N' if dy > 0 else 'S'
        else:
            desired = 'N' if dy > 0 else 'S'

        # try rotate if not facing desired
        if self.dir != desired:
            self._rotate_towards(desired)
            return True

        # if facing desired, attempt forward
        moved = self._move_forward_if_facing(world)
        if moved:
            return True

        # if can't move forward (wall or dead cell), try orthogonal directions (simple fallback)
        # try other axis
        if abs(dx) < abs(dy):
            alt = 'E' if dx > 0 else 'W'
        else:
            alt = 'N' if dy > 0 else 'S'
        if alt and self.dir != alt:
            self._rotate_towards(alt)
            return True
        else:
            # rotate once to change heading
            self.dir = self.turn_right_dir(self.dir)
            self.update_score("turn_right")
            return True

    # ----------------- DECISION RULES (local, greedy) -----------------
    def rule_pick_gold(self, world):
        if world[self.y][self.x].get("gold", False):
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
        # greedily move toward (0,0)
        return self.move_towards((0, 0), world)

    def rule_shoot_confirmed_wumpus(self, world):
        if hasattr(self, "confirmed_wumpus") and self.confirmed_wumpus and not self.arrow_used:
            wx, wy = self.confirmed_wumpus
            # Only shoot when aligned in same row or column (simple policy)
            if wx == self.x:
                dy = 1 if wy > self.y else -1
                dx = 0
            elif wy == self.y:
                dx = 1 if wx > self.x else -1
                dy = 0
            else:
                # try to move to align (greedy): prefer horizontal alignment
                # attempt to move along x toward wx
                moved = self.move_towards((wx, self.y), world)
                return moved
            # face shooting direction
            desired = None
            if dx == 1:
                desired = 'E'
            elif dx == -1:
                desired = 'W'
            elif dy == 1:
                desired = 'N'
            elif dy == -1:
                desired = 'S'
            if desired and self.dir != desired:
                self._rotate_towards(desired)
                return True
            # shoot
            self.shoot(dx, dy, world)
            self.update_score("shoot")
            self.possible_wumpus.discard(self.confirmed_wumpus)
            if self.confirmed_wumpus in self.suspicion_wumpus_count:
                del self.suspicion_wumpus_count[self.confirmed_wumpus]
            self.confirmed_wumpus = None
            return True
        return False

    def rule_move_to_safe_unvisited(self, world):
        safe_unvisited = [c for c in self.safe if c not in self.visited and c not in self.dead_cells]
        if not safe_unvisited:
            return False
        # pick nearest by Manhattan
        safe_unvisited.sort(key=lambda c: abs(c[0]-self.x) + abs(c[1]-self.y))
        target = safe_unvisited[0]
        return self.move_towards(target, world)

    def rule_move_least_risk(self, world):
        candidates = list((self.possible_pits | self.possible_wumpus) - self.visited - self.dead_cells)
        if not candidates:
            return False
        # choose candidate with minimal risk_expected_cost, break ties by Manhattan distance
        best = None
        best_metric = (math.inf, math.inf)
        for c in candidates:
            risk = self.risk_expected_cost(c)
            dist = abs(c[0]-self.x) + abs(c[1]-self.y)
            metric = (risk, dist)
            if metric < best_metric:
                best_metric = metric
                best = c
        if best is None:
            return False
        return self.move_towards(best, world)

    # ----------------- SHOOT -----------------
    def shoot(self, dx, dy, world):
        if self.arrow_used:
            return
        self.arrow_used = True
        x, y = self.x, self.y
        while 0 <= x < N and 0 <= y < N:
            x += dx
            y += dy
            if not (0 <= x < N and 0 <= y < N):
                return
            if world[y][x].get("wumpus", False):
                world[y][x]["wumpus"] = False
                # clear adjacent stenches
                for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < N and 0 <= ny < N:
                        world[ny][nx]["percept"]["stench"] = False
                return

    # ----------------- HANDLE WUMPUS MOVE -----------------
    def on_wumpus_moved(self, world):
        if hasattr(self, "confirmed_wumpus"):
            self.confirmed_wumpus = None
        self.possible_wumpus.clear()
        self.suspicion_wumpus_count.clear()
        check_cells = set(self.visited)
        check_cells.add((self.x, self.y))
        for (vx, vy) in check_cells:
            if not (0 <= vx < N and 0 <= vy < N):
                continue
            percept = world[vy][vx]["percept"]
            if percept.get("stench", False):
                for nx, ny in self.get_adjacent(vx, vy):
                    if (nx, ny) in self.safe: continue
                    if (nx, ny) in self.dead_cells: continue
                    self.possible_wumpus.add((nx, ny))
                    self.suspicion_wumpus_count[(nx, ny)] += 1
        _ = self.rule_detect_certain_wumpus(world)

    # ----------------- APPLY RULES / ACT -----------------
    def choose_and_execute_decision(self, world):
        for dr in self.decision_rules:
            performed = dr(world)
            if performed:
                return True
        return False

    def act(self, world):
        # mark visited
        self.visited.add((self.x, self.y))
        world[self.y][self.x]["visited"] = True

        # belief update
        self.apply_belief_rules(world)

        # debug print (optional)
        # print("Beliefs:", "safe", self.safe, "possible_pits", self.possible_pits, "possible_wumpus", self.possible_wumpus)

        acted = self.choose_and_execute_decision(world)
        if not acted:
            # if has gold and at exit, climb out
            if self.found_gold and (self.x, self.y) == (0, 0):
                self.climb_out(world)
            else:
                # no move available -> try exploring adjacent safe cells
                adj_safe = [c for c in self.get_adjacent(self.x, self.y) if c in self.safe and c not in self.dead_cells]
                if adj_safe:
                    # go to first adjacent safe
                    self.move_towards(adj_safe[0], world)
                else:
                    # truly stuck: do nothing
                    pass
