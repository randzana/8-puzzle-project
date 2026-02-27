import tkinter as tk
import threading
import time
import random
import heapq
import math

# --- 8-Puzzle Logic & Best-First Search ---

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def get_manhattan_distance(state):
    """Calculate the Manhattan distance heuristic for the given state."""
    distance = 0
    for i in range(9):
        if state[i] == 0:
            continue
        current_row, current_col = divmod(i, 3)
        goal_row, goal_col = divmod(state[i] - 1, 3)
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance

def is_solvable(state):
    """Check if the random board is mathematically solvable."""
    inv_count = 0
    state_list = [x for x in state if x != 0]
    for i in range(len(state_list)):
        for j in range(i + 1, len(state_list)):
            if state_list[i] > state_list[j]:
                inv_count += 1
    return inv_count % 2 == 0

def get_successors(state):
    """Generate valid moves from the current state."""
    successors = []
    empty_idx = state.index(0)
    row, col = divmod(empty_idx, 3)
    moves = [(-1, 0, 'Up'), (1, 0, 'Down'), (0, -1, 'Left'), (0, 1, 'Right')]
    for dr, dc, action in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            new_state = list(state)
            new_state[empty_idx], new_state[new_idx] = new_state[new_idx], new_state[empty_idx]
            successors.append((tuple(new_state), action))
    return successors

def best_first_search(initial_state):
    """Execute Best-First Search using Manhattan distance as the heuristic."""
    counter = 0
    frontier = []
    heapq.heappush(frontier, (get_manhattan_distance(initial_state), counter, initial_state, []))
    visited = set()
    while frontier:
        _, _, current_state, path = heapq.heappop(frontier)
        if current_state == GOAL_STATE:
            return path
        visited.add(current_state)
        for next_state, action in get_successors(current_state):
            if next_state not in visited:
                counter += 1
                heuristic = get_manhattan_distance(next_state)
                heapq.heappush(frontier, (heuristic, counter, next_state, path + [action]))
    return None

def write_solution_file(initial_state, path):
    """Write the results to solution.txt as required."""
    with open("solution.txt", "w") as f:
        f.write("--- 8-Puzzle Best-FS Solution ---\n\n")
        f.write("Initial Board:\n")
        for i in range(0, 9, 3):
            row = [" " if x == 0 else str(x) for x in initial_state[i:i+3]]
            f.write(" | ".join(row) + "\n")
            if i < 6:
                f.write("---------\n")
        if path is not None:
            f.write("\nSteps to solution:\n")
            for step, action in enumerate(path, 1):
                f.write(f"{step}. Move {action}\n")
            f.write(f"\nTotal Cost: {len(path)}\n")
        else:
            f.write("\nNo solution found.\n")


# ─────────────────────────────────────────────────
#  PREMIUM GUI IMPLEMENTATION (FLUID KINETICS)
# ─────────────────────────────────────────────────

COLORS = {
    "bg_dark":       "#0A0A12",
    "bg_card":       "#131320",
    "bg_grid":       "#0F1524",
    "accent_blue":   "#0F3460",
    "accent_cyan":   "#00E5FF",
    "accent_purple": "#8C52FF",
    "accent_pink":   "#FF3366",
    "accent_green":  "#00E676",
    "accent_gold":   "#FFD700",
    "text_primary":  "#F0F0F5",
    "text_dim":      "#6B7A90",
    "empty_tile":    "#070A11",
}

TILE_COLORS = {
    1: "#1E88E5", 2: "#43A047", 3: "#E53935",
    4: "#8E24AA", 5: "#F4511E", 6: "#00ACC1",
    7: "#D81B60", 8: "#5E35B1",
}

FONT_MAIN = ("Segoe UI", 14, "bold")
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_SUB = ("Segoe UI", 11, "bold")
FONT_TILE = ("Segoe UI", 36, "bold")

class AnimatedCanvas(tk.Canvas):
    """A canvas with a subtle animated background particle effect."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.particles = []
        self._init_particles(40)
        self._animate()

    def _init_particles(self, count):
        w, h = 600, 750
        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.uniform(1.0, 2.5)
            dx = random.uniform(-0.15, 0.15)
            dy = random.uniform(-0.6, -0.2)
            colors = ["#1a1a3a", "#10203a", "#15102a", "#2a1525", "#0a152a"]
            c = random.choice(colors)
            particle_id = self.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")
            self.particles.append({"id": particle_id, "x": x, "y": y, "r": r, "dx": dx, "dy": dy})

    def _animate(self):
        w = self.winfo_width() or 600
        h = self.winfo_height() or 950
        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            if p["y"] + p["r"] < 0:
                p["y"] = h + p["r"]
                p["x"] = random.randint(0, w)
            if p["x"] < -10: p["x"] = w + 10
            elif p["x"] > w + 10: p["x"] = -10
            self.coords(p["id"], p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"])
        self.after(30, self._animate)


class GlowButton(tk.Canvas):
    """A modern button with fluid glow/hover kinetics."""
    def __init__(self, parent, text, color, command, width=160, height=48, **kwargs):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_dark"], highlightthickness=0, **kwargs)
        self.text = text
        self.color = color
        self.command = command
        self.w, self.h = width, height
        self._hover = False
        self._disabled = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        r = 14
        w, h = self.w, self.h

        if self._disabled:
            fill, outline, text_color = "#181822", "#252533", "#454555"
        elif self._hover:
            fill, outline, text_color = self.color, self.color, "#FFFFFF"
        else:
            fill, outline, text_color = COLORS["bg_card"], self.color, self.color

        if self._hover and not self._disabled:
            for i in range(1, 4):
                self._rounded_rect(2 - i, 2 - i, w - 2 + i, h - 2 + i, r + i, "", self.color, alpha_tag=f"glow{i}")
            self.itemconfig("glow1", stipple="gray50")
            self.itemconfig("glow2", stipple="gray25")
            self.itemconfig("glow3", stipple="gray12")
            
        self._rounded_rect(2, 2, w - 2, h - 2, r, fill, outline)
        self.create_text(w // 2, h // 2, text=self.text, fill=text_color, font=FONT_MAIN)

    def _rounded_rect(self, x1, y1, x2, y2, r, fill, outline, alpha_tag=None):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        kwargs = {"fill": fill, "outline": outline, "width": 2, "smooth": True}
        if alpha_tag: kwargs["tags"] = alpha_tag
        self.create_polygon(points, **kwargs)

    def _on_enter(self, e): 
        if not self._disabled: self._hover = True; self._draw()
    def _on_leave(self, e): 
        self._hover = False; self._draw()
    def _on_click(self, e): 
        if not self._disabled and self.command: self.command()
    def set_disabled(self, disabled): 
        self._disabled = disabled; self._draw()


class PuzzleGUI:
    TILE_SIZE = 100
    TILE_GAP = 12
    GRID_PADDING = 24

    def __init__(self, root):
        self.root = root
        self.root.title("✦ Fluid 8-Puzzle Kinetics")
        self.root.geometry("520x780")
        self.root.minsize(520, 600)  # Prevents shrinking too much vertically
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        self.state = self.generate_random_board()
        self.solving = False
        self.play_again_btn = None

        self._build_ui()
        self._draw_board()

    def generate_random_board(self):
        while True:
            board = list(range(9))
            random.shuffle(board)
            if is_solvable(board):
                return tuple(board)

    def _build_ui(self):
        self.bg_canvas = AnimatedCanvas(self.root, bg=COLORS["bg_dark"], highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)

        # Header
        header = tk.Frame(self.root, bg=COLORS["bg_dark"])
        header.place(relx=0.5, rely=0.04, anchor="n")
        tk.Label(header, text="✦ 8-PUZZLE ✦", font=FONT_TITLE, bg=COLORS["bg_dark"], fg=COLORS["accent_cyan"]).pack()
        tk.Label(header, text="KINETIC SOLVER ENGINE", font=FONT_SUB, bg=COLORS["bg_dark"], fg=COLORS["text_dim"]).pack(pady=(0, 10))

        # Puzzle Grid Canvas
        grid_total = self.GRID_PADDING * 2 + self.TILE_SIZE * 3 + self.TILE_GAP * 2
        self.grid_canvas = tk.Canvas(self.root, width=grid_total, height=grid_total, bg=COLORS["bg_grid"], highlightthickness=0)
        self.grid_canvas.place(relx=0.5, rely=0.185, anchor="n")
        self._draw_rounded_rect(self.grid_canvas, 2, 2, grid_total - 2, grid_total - 2, 22, COLORS["bg_grid"], "#1A253D", 2)
        
        # User Interaction Bindings
        self.grid_canvas.bind("<ButtonPress-1>", self._on_tile_press)
        self.grid_canvas.bind("<ButtonRelease-1>", self._on_tile_release)

        # Info Panel
        info_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        info_frame.place(relx=0.5, rely=0.685, anchor="n")
        
        self.status_label = tk.Label(info_frame, text="🟢 ENGINE READY", font=FONT_MAIN, bg=COLORS["bg_dark"], fg=COLORS["accent_green"])
        self.status_label.pack()
        self.move_label = tk.Label(info_frame, text="Moves: 0", font=("Segoe UI", 12), bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
        self.move_label.pack(pady=(4, 0))
        self.heuristic_label = tk.Label(info_frame, text="Manhattan Distance: 0", font=("Segoe UI", 12), bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
        self.heuristic_label.pack()

        # Controls
        btn_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        btn_frame.place(relx=0.5, rely=0.82, anchor="n")

        self.solve_btn = GlowButton(btn_frame, "⚡ SOLVE", COLORS["accent_cyan"], self.start_solving, width=170, height=48)
        self.solve_btn.grid(row=0, column=0, padx=10)
        self.shuffle_btn = GlowButton(btn_frame, "🔀 SHUFFLE", COLORS["accent_pink"], self.shuffle_board, width=170, height=48)
        self.shuffle_btn.grid(row=0, column=1, padx=10)
        self.reset_btn = GlowButton(btn_frame, "↺ RESET TO GOAL", COLORS["accent_gold"], self.reset_to_goal, width=360, height=40)
        self.reset_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=(12, 0))

    # ── Advanced Drawing Helpers ──

    def _interpolate_color(self, c1, c2, factor):
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lighten(self, hex_color, amount):
        return self._interpolate_color(hex_color, "#FFFFFF", amount)

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, r, fill, outline, width=1, tags=None):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        kwargs = {"fill": fill, "outline": outline, "width": width, "smooth": True}
        if tags: kwargs["tags"] = tags
        canvas.create_polygon(points, **kwargs)

    def _draw_dynamic_shadow(self, x, y, radius, tag, lift_offset):
        """Simulates dynamic light casting. The shadow spreads out and drops down as the tile levitates."""
        shadow_core = "#000000"
        layers = 5 
        
        # Base shadow metrics
        base_expand = 2
        base_y_offset = 3

        # Amplified shadow metrics based on Z-axis lift
        # lift_offset is negative (moving up), so we take absolute value
        levitation_factor = abs(lift_offset) 
        
        max_expand = base_expand + (levitation_factor * 0.8)
        y_offset = base_y_offset + (levitation_factor * 1.5)

        for i in range(layers):
            factor = i / layers
            color = self._interpolate_color(shadow_core, COLORS["bg_grid"], factor)
            expand = max_expand * factor
            layer_y = y_offset * (1 - factor)
            
            self._draw_rounded_rect(self.grid_canvas, 
                                    x - expand + 2, y - expand + layer_y + 1,
                                    x + self.TILE_SIZE + expand - 2, y + self.TILE_SIZE + expand + layer_y - 1,
                                    radius + int(expand), color, "", 0, tags=tag)

    def _draw_empty_slot(self, x, y, tag):
        self._draw_rounded_rect(self.grid_canvas, x, y, x + self.TILE_SIZE, y + self.TILE_SIZE, 14, COLORS["empty_tile"], "", 0, tags=tag)
        self._draw_rounded_rect(self.grid_canvas, x, y, x + self.TILE_SIZE, y + self.TILE_SIZE, 14, "", "#030408", 2, tags=tag)
        self._draw_rounded_rect(self.grid_canvas, x+1, y+1, x + self.TILE_SIZE-1, y + self.TILE_SIZE-1, 14, "", "#1A253D", 2, tags=tag)

    def _draw_tile(self, val, x, y, tag="tiles", lift=0):
        if val == 0:
            self._draw_empty_slot(x, y, tag)
        else:
            tile_color = TILE_COLORS.get(val, "#555")
            highlight = self._lighten(tile_color, 0.25)
            
            # Dynamic Z-axis lift applied to Y coordinate
            render_y = y + lift

            # 1. Breathing Drop Shadow
            self._draw_dynamic_shadow(x, y, 14, tag, lift)

            # 2. Tile Body 
            self._draw_rounded_rect(self.grid_canvas, x, render_y, x + self.TILE_SIZE, render_y + self.TILE_SIZE,
                                    14, tile_color, "", 0, tags=tag)
            
            # 3. Inner Glass/Gloss Highlight
            self._draw_rounded_rect(self.grid_canvas, x + 2, render_y + 2, x + self.TILE_SIZE - 2, render_y + self.TILE_SIZE * 0.45,
                                    12, highlight, "", 0, tags=tag)
            
            # 4. Crisp Geometric Border
            self._draw_rounded_rect(self.grid_canvas, x + 1, render_y + 1, x + self.TILE_SIZE - 1, render_y + self.TILE_SIZE - 1,
                                    14, "", highlight, 1, tags=tag)

            # 5. Typeface
            tx, ty = x + self.TILE_SIZE // 2, render_y + self.TILE_SIZE // 2
            self.grid_canvas.create_text(tx, ty + 2, text=str(val), font=FONT_TILE, fill="#000000", tags=tag)
            self.grid_canvas.create_text(tx, ty, text=str(val), font=FONT_TILE, fill="#FFFFFF", tags=tag)

    def _draw_board(self):
        self.grid_canvas.delete("tiles")
        for i in range(9):
            row, col = divmod(i, 3)
            val = self.state[i]
            x = self.GRID_PADDING + col * (self.TILE_SIZE + self.TILE_GAP)
            y = self.GRID_PADDING + row * (self.TILE_SIZE + self.TILE_GAP)
            self._draw_tile(val, x, y, tag=f"tile_{val}" if val != 0 else "tiles")
        self.heuristic_label.config(text=f"Manhattan Distance: {get_manhattan_distance(self.state)}")

    # ── User Interaction (Manual Play) ──

    def _get_tile_at_pos(self, x, y):
        col = (x - self.GRID_PADDING) // (self.TILE_SIZE + self.TILE_GAP)
        row = (y - self.GRID_PADDING) // (self.TILE_SIZE + self.TILE_GAP)
        if 0 <= col < 3 and 0 <= row < 3:
            return row, col
        return None, None

    def _on_tile_press(self, event):
        if self.solving or self.state == GOAL_STATE: return
        
        row, col = self._get_tile_at_pos(event.x, event.y)
        if row is None: return
        
        idx = row * 3 + col
        val = self.state[idx]
        if val == 0: return

        empty_idx = self.state.index(0)
        empty_row, empty_col = divmod(empty_idx, 3)

        # Check if clicked tile is adjacent to empty slot
        if abs(row - empty_row) + abs(col - empty_col) == 1:
            self._manual_move(val, row, col, empty_row, empty_col)

    def _on_tile_release(self, event):
        pass # Reserved for future drag-and-drop if desired, tap-to-move is currently implemented.

    def _manual_move(self, tile_val, from_row, from_col, to_row, to_col):
        state_list = list(self.state)
        from_idx = from_row * 3 + from_col
        to_idx = to_row * 3 + to_col

        state_list[from_idx], state_list[to_idx] = state_list[to_idx], state_list[from_idx]
        self.state = tuple(state_list)
        
        # We manually track move count for users
        current_moves = int(self.move_label.cget("text").split(": ")[1])
        current_moves += 1
        self.move_label.config(text=f"Moves: {current_moves}")
        
        def on_slide_complete():
            self._draw_board()
            if self.state == GOAL_STATE:
                self.status_label.config(text=f"🎉 YOU SOLVED IT in {current_moves} moves!", fg=COLORS["accent_green"])
                self._show_play_again()
            else:
                self.status_label.config(text="🟢 ENGINE READY", fg=COLORS["accent_green"])

        self.status_label.config(text="🟢 PLAYER MOVING...", fg=COLORS["accent_cyan"])
        self.grid_canvas.delete(f"tile_{tile_val}")
        self._slide_tile(tile_val, from_row, from_col, to_row, to_col, on_complete=on_slide_complete)

    # ── Amplified Fluid Kinetics Engine ──

    def _slide_tile(self, tile_val, from_row, from_col, to_row, to_col, on_complete):
        from_x = self.GRID_PADDING + from_col * (self.TILE_SIZE + self.TILE_GAP)
        from_y = self.GRID_PADDING + from_row * (self.TILE_SIZE + self.TILE_GAP)
        to_x = self.GRID_PADDING + to_col * (self.TILE_SIZE + self.TILE_GAP)
        to_y = self.GRID_PADDING + to_row * (self.TILE_SIZE + self.TILE_GAP)

        dx = to_x - from_x
        dy = to_y - from_y

        duration = 0.26  # Calibrated for the Bezier curve duration
        start_time = time.time()
        max_levitation = -12.0 # Pixels the tile lifts off the ground

        tile_color = TILE_COLORS.get(tile_val, "#555")

        def animate():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                p = 1.0
            else:
                p = elapsed / duration

            # Quintic Ease-In-Out (Hyper-fluid acceleration and friction-less deceleration)
            if p < 0.5:
                progress = 16 * p**5
            else:
                progress = 1 - pow(-2 * p + 2, 5) / 2

            # Parabolic Levitation Curve (Sine wave arch over the transition)
            levitation_progress = math.sin(p * math.pi)
            current_lift = levitation_progress * max_levitation

            cur_x = from_x + dx * progress
            cur_y = from_y + dy * progress

            self.grid_canvas.delete("sliding")

            # ── Solid Motion Blur Smear Effect ──
            if 0.02 < progress < 1.0:
                steps = max(5, int(45 * progress))
                for i in range(steps):
                    f = i / (steps - 1) if steps > 1 else 0
                    trail_x = from_x + (cur_x - from_x) * f
                    trail_y = from_y + (cur_y - from_y) * f
                    
                    # Exponential fade
                    blend = f ** 2.5
                    color = self._interpolate_color(COLORS["bg_grid"], tile_color, blend * 0.95)
                    
                    self._draw_rounded_rect(
                        self.grid_canvas, 
                        trail_x, trail_y, 
                        trail_x + self.TILE_SIZE, trail_y + self.TILE_SIZE,
                        14, color, "", 0, tags="sliding"
                    )

            self._draw_tile(tile_val, cur_x, cur_y, tag="sliding", lift=current_lift)

            if p < 1.0:
                self.root.after(3, animate) # 3ms max-tick rate for zero stutter
            else:
                self.grid_canvas.delete("sliding")
                on_complete()

        # Render recessed slot instantly at source, then begin the fluid slide
        self._draw_empty_slot(from_x, from_y, "tiles")
        animate()

    # ── Logic & Flow ──

    def shuffle_board(self):
        if self.solving: return
        self._hide_play_again()
        self.state = self.generate_random_board()
        self._draw_board()
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="🔀 SHUFFLED — READY", fg=COLORS["accent_cyan"])

    def reset_to_goal(self):
        if self.solving: return
        self._hide_play_again()
        self.state = GOAL_STATE
        self._draw_board()
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="🏁 GOAL STATE", fg=COLORS["accent_gold"])

    def start_solving(self):
        if self.solving: return
        if self.state == GOAL_STATE:
            self.status_label.config(text="✅ ALREADY SOLVED!", fg=COLORS["accent_green"])
            return

        self.solving = True
        self.solve_btn.set_disabled(True)
        self.shuffle_btn.set_disabled(True)
        self.reset_btn.set_disabled(True)
        self.status_label.config(text="🔍 SEARCHING KINETICS...", fg=COLORS["accent_cyan"])

        threading.Thread(target=self._solve_logic, daemon=True).start()

    def _solve_logic(self):
        path = best_first_search(self.state)
        write_solution_file(self.state, path)

        if path is not None:
            self.root.after(0, self._animate_solution, self.state, path, 0)
        else:
            self.root.after(0, self._show_no_solution)

    def _animate_solution(self, current_state, path, step_idx):
        self.state = current_state
        self._draw_board()
        self.move_label.config(text=f"Moves: {step_idx}")

        if step_idx < len(path):
            bar = "█" * int((step_idx / len(path)) * 10) + "░" * (10 - int((step_idx / len(path)) * 10))
            self.status_label.config(text=f"⚡ Step {step_idx + 1}/{len(path)}  [{bar}]", fg=COLORS["accent_cyan"])

            action = path[step_idx]
            state_list = list(current_state)
            empty_idx = state_list.index(0)
            empty_row, empty_col = divmod(empty_idx, 3)

            if action == 'Up': tile_row, tile_col = empty_row - 1, empty_col
            elif action == 'Down': tile_row, tile_col = empty_row + 1, empty_col
            elif action == 'Left': tile_row, tile_col = empty_row, empty_col - 1
            elif action == 'Right': tile_row, tile_col = empty_row, empty_col + 1

            tile_idx = tile_row * 3 + tile_col
            tile_val = state_list[tile_idx]

            state_list[empty_idx], state_list[tile_idx] = state_list[tile_idx], state_list[empty_idx]
            next_state = tuple(state_list)

            def on_slide_complete():
                self.root.after(45, self._animate_solution, next_state, path, step_idx + 1)

            self._slide_tile(tile_val, tile_row, tile_col, empty_row, empty_col, on_slide_complete)
        else:
            self.solving = False
            self.status_label.config(text=f"🎉 SOLVED in {len(path)} moves!", fg=COLORS["accent_green"])
            self.solve_btn.set_disabled(False)
            self.shuffle_btn.set_disabled(False)
            self.reset_btn.set_disabled(False)
            self._show_play_again()

    def _show_play_again(self):
        if not self.play_again_btn:
            self.play_again_btn = GlowButton(self.solve_btn.master, "🔄 PLAY AGAIN", COLORS["accent_green"], self.shuffle_board, width=360, height=48)
            self.play_again_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=(12, 0))

    def _hide_play_again(self):
        if self.play_again_btn:
            self.play_again_btn.destroy()
            self.play_again_btn = None

    def _show_no_solution(self):
        self.solving = False
        self.status_label.config(text="❌ NO SOLUTION FOUND", fg=COLORS["accent_pink"])
        self.solve_btn.set_disabled(False)
        self.shuffle_btn.set_disabled(False)
        self.reset_btn.set_disabled(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()