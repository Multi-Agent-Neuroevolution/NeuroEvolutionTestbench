import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import numpy as np

from constants import BOUNDS, SCALE_FACTOR, PRED_SPAWN_BOUNDS, PREY_SPAWN_BOUNDS
from obstacles import Wall  # you can extend to Food or others similarly

CANVAS_SIZE = 600
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
        self.canvas = tk.Canvas(root, width=CANVAS_SIZE,
                                height=CANVAS_SIZE, bg="white")
        self.canvas.pack(side=tk.LEFT)

        # Draw grid
        for i in range(int(world_w)//20 + 1):
            x = min_x + i * 20
            cx, _ = world_to_canvas(x, min_y)
            self.canvas.create_line(cx, 0, cx, CANVAS_SIZE, fill="#ddd")
        for j in range(int(world_h)//20 + 1):
            y = min_y + j * 20
            _, cy = world_to_canvas(min_x, y)
            self.canvas.create_line(0, cy, CANVAS_SIZE, cy, fill="#ddd")

        # Buttons
        save_btn_frame = tk.Frame(root)
        save_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        tk.Button(save_btn_frame, text="Save → objects.json",
                  command=self.save).pack(fill=tk.X)
        load_btn_frame = tk.Frame(root)
        load_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Button(load_btn_frame, text="Load ← objects.json",
                  command=self.load).pack(fill=tk.X)

        # State
        self.obstacles = []      # list of Wall instances
        self.rect_map = {}       # canvas_id -> obstacle
        self._drag_data = {}     # for move and draw

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>",     self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-1>",       self.on_double_click)
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
            # zone_bounds = [x1, x2, y1, y2]
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

    def on_button_press(self, event):
        """Decide between starting a move vs. a new-rect draw."""
        # hit-test existing rectangles
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] in self.rect_map:
            self.selected_item = item[0]
            # start move
            self._drag_data["mode"] = "move"
            self._drag_data["item"] = item[0]
            self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y
            self.canvas.itemconfig(item[0], outline="red")
        else:
            # start drawing new rect
            self._drag_data["mode"] = "draw"
            self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y
            self._drag_data["rect_id"] = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline="black", dash=(2, 2)
            )

    def on_mouse_drag(self, event):

        mode = self._drag_data.get("mode")
        if mode == "draw":
            # update preview
            x0, y0 = self._drag_data["x0"], self._drag_data["y0"]
            self.canvas.coords(
                self._drag_data["rect_id"], x0, y0, event.x, event.y)
        elif mode == "move":
            # translate existing rect
            item = self._drag_data["item"]
            dx = event.x - self._drag_data["x0"]
            dy = event.y - self._drag_data["y0"]
            self.canvas.move(item, dx, dy)
            self._drag_data["x0"], self._drag_data["y0"] = event.x, event.y

    def on_button_release(self, event):
        mode = self._drag_data.get("mode")
        if mode == "draw":
            rid = self._drag_data["rect_id"]
            x1, y1, x2, y2 = self.canvas.coords(rid)
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
            self.canvas.itemconfig(rid, dash=(), fill="#faa")
            self.rect_map[rid] = wall
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

    def on_delete(self, event):
        """Delete the selected rectangle."""
        if self.selected_item and self.selected_item in self.rect_map:
            wall = self.rect_map.pop(self.selected_item)
            self.obstacles.remove(wall)
            self.canvas.delete(self.selected_item)
            self.selected_item = None

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

    def save(self):
        data = [obj.to_dict() for obj in self.obstacles]
        with open("./Objects/objects.json", "w") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", "Wrote objects.json")


if __name__ == "__main__":
    root = tk.Tk()
    Editor(root)
    root.mainloop()
