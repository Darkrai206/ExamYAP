# coding: utf-8
# license: GPLv3

import tkinter as tk
from tkinter import filedialog, ttk
import math
from solar_objects import Star, Planet, Satellite


class SolarSystem:
    def __init__(self):
        self.space_objects = []
        self.physical_time = 0
        self.perform_execution = False
        self.time_step = 1.0
        self.scale_factor = 1.0
        self.show_orbits = False
        self.orbit_limit = 500

        self.root = tk.Tk()
        self.init_gui()
        self.load_from_file("zvezdets.txt")  # Автоматическая загрузка системы

    def init_gui(self):
        self.space = tk.Canvas(self.root, width=1200, height=900, bg="black")
        self.space.pack(side=tk.TOP)

        frame = tk.Frame(self.root)
        frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = tk.Button(frame, text="Start", command=self.start_execution, width=6)
        self.start_button.pack(side=tk.LEFT)

        tk.Label(frame, text="Time step:").pack(side=tk.LEFT)
        self.time_step_var = tk.StringVar(value=str(self.time_step))
        tk.Entry(frame, textvariable=self.time_step_var, width=6).pack(side=tk.LEFT)

        tk.Label(frame, text="Speed:").pack(side=tk.LEFT)
        self.time_speed = tk.DoubleVar(value=50)
        tk.Scale(frame, variable=self.time_speed, orient=tk.HORIZONTAL,
                 from_=1, to=100, length=200).pack(side=tk.LEFT)

        tk.Button(frame, text="Open file...", command=self.open_file_dialog).pack(side=tk.LEFT)
        tk.Button(frame, text="Save to file...", command=self.save_file_dialog).pack(side=tk.LEFT)

        self.orbit_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Show orbits", variable=self.orbit_var,
                        command=self.toggle_orbits).pack(side=tk.LEFT)

        self.displayed_time = tk.StringVar(value="0.0 seconds gone")
        tk.Label(frame, textvariable=self.displayed_time, width=30).pack(side=tk.RIGHT)

    def run(self):
        """Запуск главного цикла приложения"""
        self.root.mainloop()

    def toggle_orbits(self):
        self.show_orbits = self.orbit_var.get()
        if not self.show_orbits:
            self.clear_orbits()

    def clear_orbits(self):
        for obj in self.space_objects:
            if hasattr(obj, 'orbit_id'):
                self.space.delete(obj.orbit_id)
                obj.orbit_id = None
            obj.orbit = []

    def start_execution(self):
        self.perform_execution = True
        self.start_button.config(text="Pause", command=self.stop_execution)
        self.execution()

    def stop_execution(self):
        self.perform_execution = False
        self.start_button.config(text="Start", command=self.start_execution)

    def execution(self):
        try:
            dt = float(self.time_step_var.get())
        except ValueError:
            dt = 1.0
            self.time_step_var.set(str(dt))

        self.recalculate_positions()
        self.update_positions()
        self.physical_time += dt
        self.displayed_time.set(f"{self.physical_time:.1f} seconds gone")

        if self.perform_execution:
            self.root.after(101 - int(self.time_speed.get()), self.execution)

    def recalculate_positions(self):
        for body in self.space_objects:
            self.calculate_force(body)
        for body in self.space_objects:
            self.move_space_object(body)

    def calculate_force(self, body):
        body.Fx = body.Fy = 0
        for obj in self.space_objects:
            if body == obj:
                continue

            dx = obj.x - body.x
            dy = obj.y - body.y
            r = (dx ** 2 + dy ** 2) ** 0.5
            f = 6.67408E-11 * body.m * obj.m / (r ** 2 + 1e10 ** 2)  # Добавлен смягчающий параметр

            body.Fx += f * dx / r
            body.Fy += f * dy / r

    def move_space_object(self, body):
        try:
            dt = float(self.time_step_var.get())
        except ValueError:
            dt = 1.0
            self.time_step_var.set(str(dt))

        ax = body.Fx / body.m
        ay = body.Fy / body.m

        body.Vx += ax * dt
        body.Vy += ay * dt
        body.x += body.Vx * dt
        body.y += body.Vy * dt

    def update_positions(self):
        for body in self.space_objects:
            x = self.scale_x(body.x)
            y = self.scale_y(body.y)
            r = body.R

            if self.show_orbits:
                body.orbit.append((x, y))
                if len(body.orbit) > self.orbit_limit:
                    body.orbit.pop(0)

                if len(body.orbit) > 1:
                    if hasattr(body, 'orbit_id'):
                        self.space.delete(body.orbit_id)
                    body.orbit_id = self.space.create_line(
                        body.orbit,
                        fill="gray",
                        width=1,
                        dash=(2, 2)
                    )

            if x + r < 0 or x - r > 1200 or y + r < 0 or y - r > 900:
                self.space.coords(body.image, 1200 + r, 900 + r, 1200 + 2 * r, 900 + 2 * r)
            else:
                self.space.coords(body.image, x - r, y - r, x + r, y + r)

    def clear_objects(self):
        for obj in self.space_objects:
            if hasattr(obj, 'image') and obj.image:
                self.space.delete(obj.image)
            if hasattr(obj, 'orbit_id') and obj.orbit_id:
                self.space.delete(obj.orbit_id)
        self.space_objects = []
        self.physical_time = 0

    def scale_x(self, x):
        return int(x * self.scale_factor) + 600

    def scale_y(self, y):
        return 450 - int(y * self.scale_factor)

    def open_file_dialog(self):
        self.perform_execution = False
        for obj in self.space_objects:
            self.space.delete(obj.image)

        filename = filedialog.askopenfilename(filetypes=(("Text file", ".txt"),))
        if filename:
            self.load_from_file(filename)

    def load_from_file(self, filename):
        self.clear_objects()
        try:
            with open(filename) as f:
                for line in f:
                    if not line.strip() or line[0] == '#':
                        continue

                    parts = line.split()
                    if parts[0].lower() == "star":
                        obj = Star()
                    elif parts[0].lower() == "planet":
                        obj = Planet()
                    else:
                        continue

                    obj.R = float(parts[1])
                    obj.color = parts[2]
                    obj.m = float(parts[3])
                    obj.x = float(parts[4])
                    obj.y = float(parts[5])
                    obj.Vx = float(parts[6])
                    obj.Vy = float(parts[7])

                    self.space_objects.append(obj)
                    self.create_object_image(obj)

            self.calculate_scale()
            print(f"System loaded from {filename}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def create_object_image(self, obj):
        x = self.scale_x(obj.x)
        y = self.scale_y(obj.y)
        r = obj.R
        obj.image = self.space.create_oval(x - r, y - r, x + r, y + r, fill=obj.color)

    def calculate_scale(self):
        max_dist = 0
        for obj in self.space_objects:
            dist = math.sqrt(obj.x ** 2 + obj.y ** 2)
            if dist > max_dist:
                max_dist = dist

        if max_dist == 0:
            max_dist = 1

        self.scale_factor = min(400, 300) / max_dist
        print(f"Scale factor: {self.scale_factor}")

    def save_file_dialog(self):
        filename = filedialog.asksaveasfilename(
            filetypes=(("Text file", "*.txt"),),
            defaultextension=".txt"
        )
        if filename:
            self.save_to_file(filename)

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            for obj in self.space_objects:
                f.write(
                    f"{obj.type.capitalize()} {obj.R} {obj.color} {obj.m} "
                    f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"
                )
        print(f"System saved to {filename}")


if __name__ == "__main__":
    system = SolarSystem()
    system.run()