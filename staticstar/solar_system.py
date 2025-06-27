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
        self.width = 1200
        self.height = 900
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.show_orbits = True
        self.orbit_lines = []

        self.root = tk.Tk()
        self.root.title("2D Solar System (Top View)")
        self.init_gui()
        self.load_from_file("zvezdets.txt")

    def init_gui(self):
        self.space = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.space.pack(side=tk.TOP)

        frame = tk.Frame(self.root)
        frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = tk.Button(frame, text="Start", command=self.start_execution, width=6)
        self.start_button.pack(side=tk.LEFT)

        tk.Label(frame, text="Time step:").pack(side=tk.LEFT)
        self.time_step_var = tk.DoubleVar(value=self.time_step)
        tk.Entry(frame, textvariable=self.time_step_var, width=6).pack(side=tk.LEFT)

        tk.Label(frame, text="Speed:").pack(side=tk.LEFT)
        self.time_speed = tk.DoubleVar(value=50)
        tk.Scale(frame, variable=self.time_speed, orient=tk.HORIZONTAL,
                 from_=1, to=100, length=200).pack(side=tk.LEFT)

        self.orbit_var = tk.BooleanVar(value=self.show_orbits)
        ttk.Checkbutton(frame, text="Show orbits", variable=self.orbit_var,
                        command=self.toggle_orbits).pack(side=tk.LEFT)

        self.displayed_time = tk.StringVar(value="Time: 0.0")
        tk.Label(frame, textvariable=self.displayed_time, width=15).pack(side=tk.RIGHT)

    def toggle_orbits(self):
        self.show_orbits = self.orbit_var.get()
        self.update_display()

    def run(self):
        self.root.mainloop()

    def start_execution(self):
        self.perform_execution = True
        self.start_button.config(text="Pause", command=self.stop_execution)
        self.execution()

    def stop_execution(self):
        self.perform_execution = False
        self.start_button.config(text="Start", command=self.start_execution)

    def execution(self):
        dt = self.time_step_var.get()
        self.recalculate_positions(dt)
        self.update_display()
        self.physical_time += dt
        self.displayed_time.set(f"Time: {self.physical_time:.1f}")

        if self.perform_execution:
            self.root.after(101 - int(self.time_speed.get()), self.execution)

    def recalculate_positions(self, dt):
        # Группируем планеты по их родительским звездам
        star_to_planets = {}
        for obj in self.space_objects:
            if obj.type == "star":
                star_to_planets[obj] = []

        for obj in self.space_objects:
            if hasattr(obj, 'parent_star'):
                star_to_planets[obj.parent_star].append(obj)

        # Обновляем позиции для каждой звездной системы
        for star, planets in star_to_planets.items():
            for planet in planets:
                # Определяем направление вращения (по/против часовой)
                direction = -1 if hasattr(planet, 'orbit_number') and planet.orbit_number % 2 == 0 else 1

                # Обновляем угол орбиты
                planet.orbit_angle = (planet.orbit_angle + direction * planet.orbit_speed * dt) % (2 * math.pi)

                # Обновляем позицию планеты
                planet.x = star.x + planet.orbit_radius * math.cos(planet.orbit_angle)
                planet.y = star.y + planet.orbit_radius * math.sin(planet.orbit_angle)

                # Обновляем спутники (если есть)
                if hasattr(planet, 'satellites'):
                    for sat in planet.satellites:
                        sat.orbit_angle = (sat.orbit_angle + direction * sat.orbit_speed * dt) % (2 * math.pi)
                        sat.x = planet.x + sat.orbit_radius * math.cos(sat.orbit_angle)
                        sat.y = planet.y + sat.orbit_radius * math.sin(sat.orbit_angle)

    def update_display(self):
        self.space.delete("all")
        self.orbit_lines = []

        # Рисуем орбиты если включено
        if self.show_orbits:
            for star in [obj for obj in self.space_objects if obj.type == "star"]:
                for planet in [obj for obj in self.space_objects if
                               hasattr(obj, 'parent_star') and obj.parent_star == star]:
                    x = self.scale_x(star.x)
                    y = self.scale_y(star.y)
                    r = planet.orbit_radius * self.scale_factor
                    orbit_id = self.space.create_oval(x - r, y - r, x + r, y + r, outline="gray", dash=(2, 2))
                    self.orbit_lines.append(orbit_id)

                    if hasattr(planet, 'satellites'):
                        for sat in planet.satellites:
                            x_p = self.scale_x(planet.x)
                            y_p = self.scale_y(planet.y)
                            r_s = sat.orbit_radius * self.scale_factor
                            orbit_id = self.space.create_oval(x_p - r_s, y_p - r_s, x_p + r_s, y_p + r_s,
                                                              outline="darkgray", dash=(1, 1))
                            self.orbit_lines.append(orbit_id)

        # Рисуем объекты
        for obj in self.space_objects:
            x = self.scale_x(obj.x)
            y = self.scale_y(obj.y)
            r = max(2, obj.R)

            if obj.type == "star":
                self.space.create_oval(x - r, y - r, x + r, y + r, fill=obj.color, outline="yellow")
            elif obj.type == "planet":
                self.space.create_oval(x - r, y - r, x + r, y + r, fill=obj.color)
            elif obj.type == "satellite":
                self.space.create_oval(x - r, y - r, x + r, y + r, fill=obj.color)

    def scale_x(self, x):
        return int(x * self.scale_factor) + self.center_x

    def scale_y(self, y):
        return self.center_y - int(y * self.scale_factor)

    def load_from_file(self, filename):
        self.space_objects = []
        try:
            with open(filename) as f:
                stars = []
                current_star = None

                for line in f:
                    if not line.strip() or line[0] == '#':
                        continue

                    parts = line.split()
                    if len(parts) < 8:
                        continue

                    if parts[0].lower() == "star":
                        star = Star()
                        star.R = float(parts[1])
                        star.color = parts[2]
                        star.m = float(parts[3])
                        star.x = float(parts[4])
                        star.y = float(parts[5])
                        stars.append(star)
                        self.space_objects.append(star)
                        current_star = star

                    elif parts[0].lower() == "planet":
                        planet = Planet()
                        planet.R = float(parts[1])
                        planet.color = parts[2]
                        planet.m = float(parts[3])
                        planet.x = float(parts[4])
                        planet.y = float(parts[5])
                        planet.Vx = float(parts[6])
                        planet.Vy = float(parts[7])

                        if current_star:
                            planet.parent_star = current_star
                            dx = planet.x - current_star.x
                            dy = planet.y - current_star.y
                            planet.orbit_radius = math.sqrt(dx ** 2 + dy ** 2)
                            planet.orbit_angle = math.atan2(dy, dx)
                            planet.orbit_speed = math.sqrt(planet.Vx ** 2 + planet.Vy ** 2) / planet.orbit_radius

                            # Определяем номер орбиты
                            if len(parts) > 8:
                                try:
                                    planet.orbit_number = int(parts[8].replace('star', '').replace('planet', ''))
                                except ValueError:
                                    planet.orbit_number = len([p for p in self.space_objects
                                                               if hasattr(p,
                                                                          'parent_star') and p.parent_star == current_star])

                            # Добавляем спутники
                            if len(parts) > 9 and "moon" in parts[9].lower():
                                satellite = Satellite()
                                satellite.R = 2
                                satellite.color = "gray"
                                satellite.orbit_radius = planet.orbit_radius * 0.2
                                satellite.orbit_angle = planet.orbit_angle + math.pi / 4
                                satellite.orbit_speed = planet.orbit_speed * 2
                                satellite.x = planet.x + satellite.orbit_radius * math.cos(satellite.orbit_angle)
                                satellite.y = planet.y + satellite.orbit_radius * math.sin(satellite.orbit_angle)

                                if not hasattr(planet, 'satellites'):
                                    planet.satellites = []
                                planet.satellites.append(satellite)
                                self.space_objects.append(satellite)

                        self.space_objects.append(planet)

            self.calculate_scale()
            self.update_display()
            print(
                f"System loaded successfully with {len([o for o in self.space_objects if o.type == 'star'])} stars and {len([o for o in self.space_objects if o.type == 'planet'])} planets")
        except Exception as e:
            print(f"Error loading file: {e}")

    def calculate_scale(self):
        max_dist = 0
        for star in [obj for obj in self.space_objects if obj.type == "star"]:
            for planet in [obj for obj in self.space_objects if
                           hasattr(obj, 'parent_star') and obj.parent_star == star]:
                dist = math.sqrt((planet.x - star.x) ** 2 + (planet.y - star.y) ** 2)
                if dist > max_dist:
                    max_dist = dist

        if max_dist == 0:
            max_dist = 1

        self.scale_factor = min(self.width, self.height) * 0.4 / max_dist


if __name__ == "__main__":
    system = SolarSystem()
    system.run()