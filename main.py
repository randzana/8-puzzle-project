import tkinter as tk
from tkinter import messagebox
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
        h, _, current_state, path = heapq.heappop(frontier)
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
#  PREMIUM GUI IMPLEMENTATION
# ─────────────────────────────────────────────────

# ── Color Palette ──
COLORS = {
    "bg_dark":       "#0F0F1A",
    "bg_card":       "#1A1A2E",
    "bg_grid":       "#16213E",
    "accent_blue":   "#0F3460",
    "accent_cyan":   "#00D2FF",
    "accent_purple": "#7B2FF7",
    "accent_pink":   "#E94560",
    "accent_green":  "#00E676",
    "accent_gold":   "#FFD700",
    "text_primary":  "#E8E8F0",
    "text_dim":      "#7F8C9B",
    "tile_1":        "#1E88E5",
    "tile_2":        "#43A047",
    "tile_3":        "#E53935",
    "tile_4":        "#8E24AA",
    "tile_5":        "#FB8C00",
    "tile_6":        "#00ACC1",
    "tile_7":        "#D81B60",
    "tile_8":        "#5E35B1",
    "empty_tile":    "#0D1117",
}

TILE_COLORS = {
    1: "#1E88E5", 2: "#43A047", 3: "#E53935",
    4: "#8E24AA", 5: "#FB8C00", 6: "#00ACC1",
    7: "#D81B60", 8: "#5E35B1",
}


class AnimatedCanvas(tk.Canvas):
    """A canvas with a subtle animated background particle effect."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.particles = []
        self._init_particles(30)
        self._animate()

    def _init_particles(self, count):
        w = 600
        h = 750
        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.uniform(1, 3)
            dx = random.uniform(-0.3, 0.3)
            dy = random.uniform(-0.5, -0.1)
            alpha_hex = random.choice(["15", "20", "28", "30", "38"])
            color = f"#{'7B2FF7'[:2]}{alpha_hex}{'F7'[-2:]}"
            colors = ["#2a1a4a", "#1a2a4a", "#1a3a3a", "#2a2a3a", "#3a1a3a"]
            c = random.choice(colors)
            particle_id = self.create_oval(x - r, y - r, x + r, y + r, fill=c, outline="")
            self.particles.append({"id": particle_id, "x": x, "y": y, "r": r,
                                   "dx": dx, "dy": dy, "color": c})

    def _animate(self):
        w = self.winfo_width() or 600
        h = self.winfo_height() or 750
        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            if p["y"] + p["r"] < 0:
                p["y"] = h + p["r"]
                p["x"] = random.randint(0, w)
            if p["x"] < -10:
                p["x"] = w + 10
            elif p["x"] > w + 10:
                p["x"] = -10
            self.coords(p["id"], p["x"] - p["r"], p["y"] - p["r"],
                        p["x"] + p["r"], p["y"] + p["r"])
        self.after(50, self._animate)


class GlowButton(tk.Canvas):
    """A modern button with glow/hover effects drawn on a Canvas."""

    def __init__(self, parent, text, color, command, width=160, height=48, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS["bg_dark"], highlightthickness=0, **kwargs)
        self.text = text
        self.color = color
        self.command = command
        self.w = width
        self.h = height
        self._hover = False
        self._disabled = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        r = 12  # corner radius
        w, h = self.w, self.h

        if self._disabled:
            fill = "#333340"
            outline = "#444455"
            text_color = "#666670"
        elif self._hover:
            fill = self.color
            outline = self.color
            text_color = "#FFFFFF"
        else:
            fill = COLORS["bg_card"]
            outline = self.color
            text_color = self.color

        # Rounded rectangle
        self._rounded_rect(2, 2, w - 2, h - 2, r, fill, outline)

        # Glow effect on hover
        if self._hover and not self._disabled:
            for i in range(3):
                alpha_colors = {"#00D2FF": ["#002a3a", "#001a2a", "#001020"],
                                "#E94560": ["#3a0a15", "#2a0510", "#1a0308"],
                                "#00E676": ["#003a1a", "#002a10", "#001a08"],
                                "#FFD700": ["#3a3000", "#2a2200", "#1a1500"]}
                glow = alpha_colors.get(self.color, ["#1a1a2e", "#151520", "#101018"])
                self._rounded_rect(2 - i * 2, 2 - i * 2, w - 2 + i * 2, h - 2 + i * 2,
                                    r + i, "", glow[i])

            # Redraw the main rect on top
            self._rounded_rect(2, 2, w - 2, h - 2, r, fill, outline)

        # Text
        self.create_text(w // 2, h // 2, text=self.text, fill=text_color,
                         font=("Helvetica Neue", 14, "bold"))

    def _rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]
        self.create_polygon(points, fill=fill, outline=outline, width=2, smooth=True)

    def _on_enter(self, event):
        if not self._disabled:
            self._hover = True
            self._draw()

    def _on_leave(self, event):
        self._hover = False
        self._draw()

    def _on_click(self, event):
        if not self._disabled and self.command:
            self.command()

    def set_disabled(self, disabled):
        self._disabled = disabled
        self._draw()


class PuzzleGUI:
    """A premium, beautifully designed 8-Puzzle Solver GUI."""

    TILE_SIZE = 100
    TILE_GAP = 8
    GRID_PADDING = 20

    def __init__(self, root):
        self.root = root
        self.root.title("✦ 8-Puzzle Solver — Best-First Search")
        self.root.geometry("520x780")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(False, False)

        self.state = self.generate_random_board()
        self.move_count = 0
        self.solving = False
        self.glow_animation_id = None

        self._build_ui()
        self._draw_board()
        self._start_idle_glow()

    # ── Board generation ──

    def generate_random_board(self):
        while True:
            board = list(range(9))
            random.shuffle(board)
            if is_solvable(board):
                return tuple(board)

    # ── UI Construction ──

    def _build_ui(self):
        # Background animated canvas
        self.bg_canvas = AnimatedCanvas(self.root, bg=COLORS["bg_dark"], highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)

        # ── Header ──
        header_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        header_frame.place(relx=0.5, y=25, anchor="n")

        # Title with gradient-like multi-color effect
        title_line1 = tk.Label(header_frame, text="✦  8-PUZZLE  ✦",
                               font=("Helvetica Neue", 28, "bold"),
                               bg=COLORS["bg_dark"], fg=COLORS["accent_cyan"])
        title_line1.pack()

        subtitle = tk.Label(header_frame, text="BEST-FIRST SEARCH SOLVER",
                            font=("Helvetica Neue", 11, "bold"),
                            bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
        subtitle.pack(pady=(2, 0))

        # Decorative line
        line_canvas = tk.Canvas(header_frame, width=280, height=3,
                                bg=COLORS["bg_dark"], highlightthickness=0)
        line_canvas.pack(pady=(8, 0))
        # Gradient line
        for i in range(280):
            ratio = i / 280
            if ratio < 0.5:
                r = int(0x0F + (0x00 - 0x0F) * ratio * 2)
                g = int(0x34 + (0xD2 - 0x34) * ratio * 2)
                b = int(0x60 + (0xFF - 0x60) * ratio * 2)
            else:
                r = int(0x00 + (0x7B - 0x00) * (ratio - 0.5) * 2)
                g = int(0xD2 + (0x2F - 0xD2) * (ratio - 0.5) * 2)
                b = int(0xFF + (0xF7 - 0xFF) * (ratio - 0.5) * 2)
            color = f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
            line_canvas.create_line(i, 0, i, 3, fill=color)

        # ── Puzzle Grid (Canvas-based) ──
        grid_total = self.GRID_PADDING * 2 + self.TILE_SIZE * 3 + self.TILE_GAP * 2
        self.grid_canvas = tk.Canvas(self.root, width=grid_total, height=grid_total,
                                     bg=COLORS["bg_grid"], highlightthickness=0)
        self.grid_canvas.place(relx=0.5, y=150, anchor="n")

        # Draw rounded border for grid
        self._draw_rounded_rect(self.grid_canvas, 2, 2, grid_total - 2, grid_total - 2,
                                15, COLORS["bg_grid"], COLORS["accent_blue"], 2)

        # ── Info Panel ──
        info_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        info_frame.place(relx=0.5, y=520, anchor="n")

        # Status
        self.status_label = tk.Label(info_frame, text="🟢  READY",
                                     font=("Helvetica Neue", 14, "bold"),
                                     bg=COLORS["bg_dark"], fg=COLORS["accent_green"])
        self.status_label.pack()

        # Move counter
        self.move_label = tk.Label(info_frame, text="Moves: 0",
                                   font=("Helvetica Neue", 11),
                                   bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
        self.move_label.pack(pady=(4, 0))

        # Heuristic value
        h = get_manhattan_distance(self.state)
        self.heuristic_label = tk.Label(info_frame, text=f"Manhattan Distance: {h}",
                                        font=("Helvetica Neue", 11),
                                        bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
        self.heuristic_label.pack(pady=(2, 0))

        # ── Buttons ──
        btn_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        btn_frame.place(relx=0.5, y=630, anchor="n")

        self.solve_btn = GlowButton(btn_frame, "⚡ SOLVE", COLORS["accent_cyan"],
                                    self.start_solving, width=180, height=50)
        self.solve_btn.grid(row=0, column=0, padx=12)

        self.shuffle_btn = GlowButton(btn_frame, "🔀 SHUFFLE", COLORS["accent_pink"],
                                      self.shuffle_board, width=180, height=50)
        self.shuffle_btn.grid(row=0, column=1, padx=12)

        # Reset button (smaller, below)
        self.reset_btn = GlowButton(btn_frame, "↺ RESET TO GOAL", COLORS["accent_gold"],
                                    self.reset_to_goal, width=376, height=40)
        self.reset_btn.grid(row=1, column=0, columnspan=2, padx=12, pady=(12, 0))

        # ── Footer ──
        footer = tk.Label(self.root, text="Algorithm: Greedy Best-First Search  ·  Heuristic: Manhattan Distance",
                          font=("Helvetica Neue", 9),
                          bg=COLORS["bg_dark"], fg="#3a3a50")
        footer.place(relx=0.5, y=750, anchor="s")

    # ── Drawing helpers ──

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, r, fill, outline, width=1):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]
        canvas.create_polygon(points, fill=fill, outline=outline, width=width, smooth=True)

    def _draw_board(self):
        self.grid_canvas.delete("tiles")
        for i in range(9):
            row, col = divmod(i, 3)
            val = self.state[i]
            x = self.GRID_PADDING + col * (self.TILE_SIZE + self.TILE_GAP)
            y = self.GRID_PADDING + row * (self.TILE_SIZE + self.TILE_GAP)

            if val == 0:
                # Empty tile — subtle inset
                self._draw_rounded_rect(self.grid_canvas, x + 2, y + 2,
                                        x + self.TILE_SIZE - 2, y + self.TILE_SIZE - 2,
                                        10, COLORS["empty_tile"], "#1a1a30", 1)
                self.grid_canvas.create_text(x + self.TILE_SIZE // 2, y + self.TILE_SIZE // 2,
                                             text="", tags="tiles")
            else:
                tile_color = TILE_COLORS.get(val, "#555")

                # Shadow
                self._draw_rounded_rect(self.grid_canvas, x + 3, y + 3,
                                        x + self.TILE_SIZE + 1, y + self.TILE_SIZE + 1,
                                        10, "#08080F", "", 0)

                # Tile body
                self._draw_rounded_rect(self.grid_canvas, x, y,
                                        x + self.TILE_SIZE, y + self.TILE_SIZE,
                                        10, tile_color, "", 0)

                # Highlight (top-left shine)
                highlight_color = self._lighten(tile_color, 0.25)
                self._draw_rounded_rect(self.grid_canvas, x + 3, y + 3,
                                        x + self.TILE_SIZE - 3, y + self.TILE_SIZE * 0.45,
                                        8, "", "", 0)

                # Number
                self.grid_canvas.create_text(x + self.TILE_SIZE // 2,
                                             y + self.TILE_SIZE // 2,
                                             text=str(val),
                                             font=("Helvetica Neue", 32, "bold"),
                                             fill="#FFFFFF", tags="tiles")

                # Subtle inner border highlight
                self._draw_rounded_rect(self.grid_canvas, x + 1, y + 1,
                                        x + self.TILE_SIZE - 1, y + self.TILE_SIZE - 1,
                                        10, "", highlight_color, 1)

        # Update heuristic
        h = get_manhattan_distance(self.state)
        self.heuristic_label.config(text=f"Manhattan Distance: {h}")

    def _lighten(self, hex_color, amount):
        """Lighten a hex color by a given amount (0-1)."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Idle glow animation around the grid ──

    def _start_idle_glow(self):
        self._glow_step = 0
        self._pulse_glow()

    def _pulse_glow(self):
        if self.solving:
            self.glow_animation_id = self.root.after(100, self._pulse_glow)
            return
        # Subtle pulsing border on the grid
        self._glow_step = (self._glow_step + 1) % 60
        intensity = int(20 + 15 * math.sin(self._glow_step * math.pi / 30))
        border_color = f"#{intensity:02x}{intensity + 20:02x}{intensity + 40:02x}"
        grid_total = self.GRID_PADDING * 2 + self.TILE_SIZE * 3 + self.TILE_GAP * 2
        self.grid_canvas.delete("glow_border")
        points = self._rounded_rect_points(1, 1, grid_total - 1, grid_total - 1, 15)
        self.grid_canvas.create_polygon(points, fill="", outline=border_color,
                                        width=2, smooth=True, tags="glow_border")
        self.glow_animation_id = self.root.after(80, self._pulse_glow)

    def _rounded_rect_points(self, x1, y1, x2, y2, r):
        return [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]

    # ── Actions ──

    def shuffle_board(self):
        if self.solving:
            return
        self.state = self.generate_random_board()
        self.move_count = 0
        self._draw_board()
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="🔀  SHUFFLED — READY", fg=COLORS["accent_cyan"])

    def reset_to_goal(self):
        if self.solving:
            return
        self.state = GOAL_STATE
        self.move_count = 0
        self._draw_board()
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="🏁  GOAL STATE", fg=COLORS["accent_gold"])

    def start_solving(self):
        if self.solving:
            return
        if self.state == GOAL_STATE:
            self.status_label.config(text="✅  ALREADY SOLVED!", fg=COLORS["accent_green"])
            return

        self.solving = True
        self.solve_btn.set_disabled(True)
        self.shuffle_btn.set_disabled(True)
        self.reset_btn.set_disabled(True)
        self.status_label.config(text="🔍  SEARCHING...", fg=COLORS["accent_cyan"])

        thread = threading.Thread(target=self._solve_logic, daemon=True)
        thread.start()

    def _solve_logic(self):
        initial_state = self.state
        path = best_first_search(initial_state)
        write_solution_file(initial_state, path)

        if path is not None:
            self.root.after(0, self._animate_solution, initial_state, path, 0)
        else:
            self.root.after(0, self._show_no_solution)

    def _animate_solution(self, current_state, path, step_idx):
        self.state = current_state
        self._draw_board()
        self.move_count = step_idx
        self.move_label.config(text=f"Moves: {step_idx}")

        if step_idx < len(path):
            progress = step_idx / len(path)
            bar = "█" * int(progress * 10) + "░" * (10 - int(progress * 10))
            self.status_label.config(
                text=f"⚡ Step {step_idx + 1}/{len(path)}  [{bar}]",
                fg=COLORS["accent_cyan"]
            )

            action = path[step_idx]
            state_list = list(current_state)
            empty_idx = state_list.index(0)
            row, col = divmod(empty_idx, 3)

            if action == 'Up': next_row, next_col = row - 1, col
            elif action == 'Down': next_row, next_col = row + 1, col
            elif action == 'Left': next_row, next_col = row, col - 1
            elif action == 'Right': next_row, next_col = row, col + 1

            next_idx = next_row * 3 + next_col
            state_list[empty_idx], state_list[next_idx] = state_list[next_idx], state_list[empty_idx]
            next_state = tuple(state_list)

            self.root.after(400, self._animate_solution, next_state, path, step_idx + 1)
        else:
            self.solving = False
            self.status_label.config(
                text=f"🎉  SOLVED in {len(path)} moves!",
                fg=COLORS["accent_green"]
            )
            self.move_label.config(text=f"Moves: {len(path)}")
            self.solve_btn.set_disabled(False)
            self.shuffle_btn.set_disabled(False)
            self.reset_btn.set_disabled(False)
            # Celebration flash
            self._celebrate(0)

    def _celebrate(self, step):
        """Quick color flash celebration on solve."""
        if step >= 6:
            self._draw_board()
            return
        colors = [COLORS["accent_green"], COLORS["accent_cyan"],
                  COLORS["accent_gold"], COLORS["accent_purple"],
                  COLORS["accent_pink"], COLORS["accent_green"]]
        grid_total = self.GRID_PADDING * 2 + self.TILE_SIZE * 3 + self.TILE_GAP * 2
        self.grid_canvas.delete("glow_border")
        points = self._rounded_rect_points(0, 0, grid_total, grid_total, 15)
        self.grid_canvas.create_polygon(points, fill="", outline=colors[step],
                                        width=3, smooth=True, tags="glow_border")
        self.root.after(200, self._celebrate, step + 1)

    def _show_no_solution(self):
        self.solving = False
        self.status_label.config(text="❌  NO SOLUTION FOUND", fg=COLORS["accent_pink"])
        self.solve_btn.set_disabled(False)
        self.shuffle_btn.set_disabled(False)
        self.reset_btn.set_disabled(False)


# ── Launch ──

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
