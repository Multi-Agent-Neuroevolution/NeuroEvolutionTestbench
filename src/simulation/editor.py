import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import numpy as np

from constants import BOUNDS, SCALE_FACTOR, PRED_SPAWN_BOUNDS, PREY_SPAWN_BOUNDS
from obstacles import Wall

CANVAS_SIZE = 800
scaled_bounds = [v * SCALE_FACTOR for v in BOUNDS]
min_x, max_x, min_y, max_y = scaled_bounds
world_w = max_x - min_x
world_h = max_y - min_y

sx = CANVAS_SIZE / world_w
sy = CANVAS_SIZE / world_h
scale = min(sx, sy)
extra_x = (CANVAS_SIZE - world_w * scale) / 2
extra_y = (CANVAS_SIZE - world_h * scale) / 2


def world_to_canvas(wx, wy):
    cx = (wx - min_x) * scale + extra_x
    cy = (wy - min_y) * scale + extra_y
    return cx, cy


def canvas_to_world(cx, cy):
    wx = (cx - extra_x) / scale + min_x
    wy = (cy - extra_y) / scale + min_y
    return wx, wy


class Editor:
    def __init__(self, root):
        self.root = root
        self.root.title("Obstacle Editor")
        self.root.geometry("1000x800")

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Save objects.json",
                   command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Center",
                   command=lambda: self.center_view()).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load objects.json",
                   command=self.load).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # Items menu
        itemmenue = tk.Menubutton(btn_frame, text="Draw Tools ▼", relief=tk.RAISED,
                                  borderwidth=1, padx=10, pady=5)
        itemmenue.menu = tk.Menu(itemmenue, tearoff=0)
        itemmenue["menu"] = itemmenue.menu

        # status indicator for the current draw mode
        self.draw_mode_var = tk.StringVar(value="Mode: None")
        status_lbl = ttk.Label(btn_frame, textvariable=self.draw_mode_var)
        status_lbl.pack(side=tk.RIGHT, padx=10)

        # helper to pick an item and update the status label
        def _pick(kind):
            display_names = {
                "prey_spawn": "Prey Spawn Zone",
                "pred_spawn": "Predator Spawn Zone",
                "wall": "Wall",
                "food_spawn": "Food Spawn Zone",
                "move": "Move/Select",
            }
            if kind != "move":
                self.start_drawing(kind)
            self.draw_mode_var.set(f"Mode: {display_names.get(kind, kind)}")

        itemmenue.menu.add_command(label="Prey Spawn Zone",
                                   command=lambda: _pick("prey_spawn"))
        itemmenue.menu.add_command(label="Predator Spawn Zone",
                                   command=lambda: _pick("pred_spawn"))
        itemmenue.menu.add_command(label="Wall",
                                   command=lambda: _pick("wall"))
        itemmenue.menu.add_command(label="Food Spawn Zone",
                                   command=lambda: _pick("food_spawn"))
        itemmenue.pack(side=tk.LEFT, padx=5)

        # Canvas frame with border
        canvas_frame = ttk.LabelFrame(
            main_frame, text="World View", padding="10")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Now create the canvas inside the frame
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE,
                                height=CANVAS_SIZE, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw grid
        for i in range(int(world_w) // 20 + 1):
            x = min_x + i * 20
            cx, _ = world_to_canvas(x, min_y)
            self.canvas.create_line(cx, 0, cx, CANVAS_SIZE, fill="#ddd")
        for j in range(int(world_h) // 20 + 1):
            y = min_y + j * 20
            _, cy = world_to_canvas(min_x, y)
            self.canvas.create_line(0, cy, CANVAS_SIZE, cy, fill="#ddd")

        # State
        self.obstacles = []      # list of Wall instances
        self.rect_map = {}       # canvas_id -> obstacle
        self._drag_data = {}     # for move and draw
        self.selected_item = None

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>",     self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-1>",       self.on_double_click)
        self.canvas.bind("<MouseWheel>",    self.on_zoom)
        self.canvas.bind("<Escape>", lambda e: _pick("move"))
        self.canvas.focus_set()
        self.canvas.bind("<Delete>", self.on_delete)

        # Create two transparent rectangles to represent the spawn bounds
        prey_bounds = [v * SCALE_FACTOR for v in PREY_SPAWN_BOUNDS]
        pred_bounds = [v * SCALE_FACTOR for v in PRED_SPAWN_BOUNDS]
        prey_bounds = [min_x + prey_bounds[0], min_y + prey_bounds[1],
                       min_x + prey_bounds[2], min_y + prey_bounds[3]]
        pred_bounds = [min_x + pred_bounds[0], min_y + pred_bounds[1],
                       min_x + pred_bounds[2], min_y + pred_bounds[3]]

        def _draw_zone(zone_bounds, color):
            # zone_bounds = [x1, x2, y1, y2] in world coords
            x1, x2, y1, y2 = zone_bounds
            xmin, xmax = sorted((x1, x2))
            ymin, ymax = sorted((y1, y2))
            cx1, cy1 = world_to_canvas(xmin, ymin)
            cx2, cy2 = world_to_canvas(xmax, ymax)
            # stipple gives you “transparency” on Tk canvas
            self.canvas.create_rectangle(
                cx1, cy1, cx2, cy2,
                fill='',
                stipple='gray25',
                outline=color
            )

        _draw_zone(PREY_SPAWN_BOUNDS, 'green')
        _draw_zone(PRED_SPAWN_BOUNDS, 'red')

        # Ensure the canvas has a sensible scrollregion (required for panning/view)
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    def center_view(self):
        # center view to the middle of the scrollregion or canvas
        bbox = self.canvas.cget("scrollregion")
        if bbox:
            x0, y0, x1, y1 = map(int, bbox.split())
            w = x1 - x0
            h = y1 - y0
            # move so center of scrollregion is centered in viewport
            self.canvas.xview_moveto((x0 + w/2 - CANVAS_SIZE/2) / max(1, w))
            self.canvas.yview_moveto((y0 + h/2 - CANVAS_SIZE/2) / max(1, h))
        else:
            # fallback
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)

    def start_drawing(self, kind):
        # Set the drawing mode
        self._drag_data["mode"] = "draw"
        self._drag_data["kind"] = kind
        self.selected_item = None  # Clear any selection

    def on_button_press(self, event):
        """Decide between starting a move vs. a new-rect draw or pan."""
        # Check if we're in draw mode first
        if self._drag_data.get("mode") == "draw":
            # Start drawing a new rectangle
            self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y
            kind = self._drag_data.get("kind", "wall")
            # Pick color based on kind
            if kind == "wall":
                color = "#faa"
            elif kind == "prey_spawn":
                color = "#afa"
            elif kind == "pred_spawn":
                color = "#ffa"
            elif kind == "food_spawn":
                color = "#aaf"
            else:
                color = "#ccc"
            rid = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline="black", fill=color, dash=(2, 2)
            )
            self._drag_data["rect_id"] = rid
            return

        # hit-test existing rectangles
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] in self.rect_map:
            # Check if we actually clicked on the rectangle (within 5 pixels)
            coords = self.canvas.coords(item[0])
            if coords:
                x1, y1, x2, y2 = coords
                if (min(x1, x2) - 5 <= event.x <= max(x1, x2) + 5 and
                        min(y1, y2) - 5 <= event.y <= max(y1, y2) + 5):
                    self.selected_item = item[0]
                    # start move
                    self._drag_data["mode"] = "move"
                    self._drag_data["item"] = item[0]
                    self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y
                    self.canvas.itemconfig(item[0], outline="red")
                    return

        # Otherwise start panning
        self._drag_data["mode"] = "pan"
        self.canvas.scan_mark(event.x, event.y)

    def on_mouse_drag(self, event):
        mode = self._drag_data.get("mode")
        if mode == "move":
            # translate existing rect (canvas coordinates)
            item = self._drag_data["item"]
            dx = event.x - self._drag_data["x0"]
            dy = event.y - self._drag_data["y0"]
            self.canvas.move(item, dx, dy)
            # update drag origin
            self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y
            # Update the underlying Wall position
            if item in self.rect_map:
                wall = self.rect_map[item]
                coords = self.canvas.coords(item)
                if coords:
                    x1, y1, x2, y2 = coords
                    wx1, wy1 = canvas_to_world(x1, y1)
                    wall.pos = np.array([wx1, wy1])
        elif mode == "pan":
            # use native canvas scanning for smooth panning
            self.canvas.scan_dragto(event.x, event.y, gain=1)
        elif mode == "draw":
            # Update the rectangle being drawn
            if "rect_id" in self._drag_data:
                rid = self._drag_data["rect_id"]
                x0, y0 = self._drag_data["x0"], self._drag_data["y0"]
                self.canvas.coords(rid, x0, y0, event.x, event.y)

    def on_button_release(self, event):
        mode = self._drag_data.get("mode")
        if mode == "draw":
            if "rect_id" not in self._drag_data:
                self._drag_data.clear()
                return

            rid = self._drag_data["rect_id"]
            coords = self.canvas.coords(rid)
            if not coords:
                self.canvas.delete(rid)
                self._drag_data.clear()
                return

            x1, y1, x2, y2 = coords
            # Check if rectangle is too small (less than 5 pixels)
            if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
                self.canvas.delete(rid)
                self._drag_data.clear()
                return

            # normalize coords
            cx1, cy1 = min(x1, x2), min(y1, y2)
            cx2, cy2 = max(x1, x2), max(y1, y2)
            # convert to world
            wx1, wy1 = canvas_to_world(cx1, cy1)
            wx2, wy2 = canvas_to_world(cx2, cy2)
            w, h = wx2 - wx1, wy2 - wy1
            # create real obstacle
            wall = Wall(pos=np.array([wx1, wy1]), width=w, height=h)
            self.obstacles.append(wall)
            # finalize rect appearance
            kind = self._drag_data.get("kind", "wall")
            if kind == "wall":
                color = "#faa"
            elif kind == "prey_spawn":
                color = "#afa"
            elif kind == "pred_spawn":
                color = "#ffa"
            elif kind == "food_spawn":
                color = "#aaf"
            else:
                color = "#ccc"
            self.canvas.itemconfig(rid, dash=(), fill=color)
            self.rect_map[rid] = wall

            # update scrollregion after adding an item
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

        elif mode == "move":
            # Reset outline color when done moving
            if "item" in self._drag_data and self._drag_data["item"] in self.rect_map:
                self.canvas.itemconfig(
                    self._drag_data["item"], outline="black")

        # clear drag
        self._drag_data.clear()

    def on_double_click(self, event):
        """Resize the rectangle via prompt."""
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] in self.rect_map:
            wall = self.rect_map[item[0]]
            ans = simpledialog.askstring("Resize",
                                         f"Current W×H = {wall.width:.1f}×{wall.height:.1f}\nEnter new width,height:")
            if not ans:
                return
            try:
                nw, nh = map(float, ans.split(","))
            except:
                messagebox.showerror(
                    "Error", "Invalid format. Use width,height")
                return
            wall.width, wall.height = nw, nh
            # update canvas rect
            # keep same top-left
            cx, cy = world_to_canvas(*wall.pos)
            cx2, cy2 = world_to_canvas(wall.pos[0]+nw, wall.pos[1]+nh)
            self.canvas.coords(item[0], cx, cy, cx2, cy2)

    def on_zoom(self, event):
        # Zoom the canvas view
        factor = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", event.x, event.y, factor, factor)
        # after scaling, update the scrollregion so panning remains sensible
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    def on_delete(self, event):
        """Delete the selected rectangle."""
        if self.selected_item and self.selected_item in self.rect_map:
            wall = self.rect_map.pop(self.selected_item)
            try:
                self.obstacles.remove(wall)
            except ValueError:
                pass
            self.canvas.delete(self.selected_item)
            self.selected_item = None
            # update scrollregion
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

    def load(self):
        """Load obstacles from objects.json."""
        try:
            with open("./Objects/objects.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "objects.json not found")
            return
        for obj in data:
            if obj["type"] == "Rectangle":
                wall = Wall(pos=np.array([obj["x"], obj["y"]]),
                            width=obj["width"], height=obj["height"])
                self.obstacles.append(wall)
                cx, cy = world_to_canvas(obj["x"], obj["y"])
                cx2, cy2 = world_to_canvas(
                    obj["x"] + obj["width"], obj["y"] + obj["height"])
                rid = self.canvas.create_rectangle(
                    cx, cy, cx2, cy2, outline="black", fill="#faa")
                self.rect_map[rid] = wall
        # update scrollregion after loading
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    def save(self):
        data = [obj.to_dict() for obj in self.obstacles]
        with open("./Objects/objects.json", "w") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", "Wrote objects.json")

    def clear_all(self):
        """Clear all added objects from the canvas."""
        # Ask for confirmation
        if not messagebox.askyesno("Clear All", "Are you sure you want to clear all objects?"):
            return

        # Delete all rectangles from canvas
        for rid in list(self.rect_map.keys()):
            self.canvas.delete(rid)

        # Clear all data structures
        self.obstacles.clear()
        self.rect_map.clear()
        self.selected_item = None
        self._drag_data.clear()

        # Update scrollregion
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)


if __name__ == "__main__":
    root = tk.Tk()
    Editor(root)
    root.mainloop()
