# coding: utf-8
# license: GPLv3

import tkinter as tk
from tkinter import filedialog
from solar_objects import Star, Planet


class SolarSystem:
    def __init__(self):
        self.space_objects = []
        self.physical_time = 0
        self.perform_execution = False
        self.time_step = 1.0
        self.scale_factor = 1.0

        self.root = tk.Tk()
        self.init_gui()

    def init_gui(self):
        #Инициализация графического интерфейса
        self.space = tk.Canvas(self.root, width=1200, height=900, bg="black")
        self.space.pack(side=tk.TOP)

        frame = tk.Frame(self.root)
        frame.pack(side=tk.BOTTOM)

        self.start_button = tk.Button(frame, text="Start", command=self.start_execution, width=6)
        self.start_button.pack(side=tk.LEFT)

        self.time_step_var = tk.DoubleVar(value=self.time_step)
        tk.Entry(frame, textvariable=self.time_step_var).pack(side=tk.LEFT)

        self.time_speed = tk.DoubleVar()
        tk.Scale(frame, variable=self.time_speed, orient=tk.HORIZONTAL).pack(side=tk.LEFT)

        tk.Button(frame, text="Open file...", command=self.open_file_dialog).pack(side=tk.LEFT)
        tk.Button(frame, text="Save to file...", command=self.save_file_dialog).pack(side=tk.LEFT)

        self.displayed_time = tk.StringVar(value="0.0 seconds gone")
        tk.Label(frame, textvariable=self.displayed_time, width=30).pack(side=tk.RIGHT)

    def save_file_dialog(self):
        #Сохранение системы в файл
        filename = filedialog.asksaveasfilename(
            filetypes=(("Text file", "*.txt"),),
            defaultextension=".txt"
        )
        if filename:
            self.save_to_file(filename)

    def save_to_file(self, filename):
        #Сохранение объектов системы в файл
        with open(filename, 'w') as f:
            for obj in self.space_objects:
                f.write(
                    f"{obj.type.capitalize()} {obj.R} {obj.color} {obj.m} "
                    f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"
                )
        print(f"System saved to {filename}")

        frame = tk.Frame(self.root)
        frame.pack(side=tk.BOTTOM)

        # Кнопки управления
        self.start_button = tk.Button(frame, text="Start", command=self.start_execution, width=6)
        self.start_button.pack(side=tk.LEFT)

        self.time_step_var = tk.DoubleVar(value=self.time_step)
        tk.Entry(frame, textvariable=self.time_step_var).pack(side=tk.LEFT)

        self.time_speed = tk.DoubleVar()
        tk.Scale(frame, variable=self.time_speed, orient=tk.HORIZONTAL).pack(side=tk.LEFT)

        tk.Button(frame, text="Open file...", command=self.open_file_dialog).pack(side=tk.LEFT)
        tk.Button(frame, text="Save to file...", command=self.save_file_dialog).pack(side=tk.LEFT)

        self.displayed_time = tk.StringVar(value="0.0 seconds gone")
        tk.Label(frame, textvariable=self.displayed_time, width=30).pack(side=tk.RIGHT)

    def run(self):
        #Запуск главного цикла
        self.root.mainloop()

    def execution(self):
        #Основной цикл выполнения
        self.recalculate_positions()
        self.update_positions()
        self.physical_time += self.time_step_var.get()
        self.displayed_time.set(f"{self.physical_time:.1f} seconds gone")

        if self.perform_execution:
            self.root.after(101 - int(self.time_speed.get()), self.execution)

    def recalculate_positions(self):
        #Пересчет позиций объектов
        for body in self.space_objects:
            self.calculate_force(body)
        for body in self.space_objects:
            self.move_space_object(body)

    def calculate_force(self, body):
        #Расчет сил для одного тела
        body.Fx = body.Fy = 0
        for obj in self.space_objects:
            if body == obj:
                continue

            dx = obj.x - body.x
            dy = obj.y - body.y
            r = (dx ** 2 + dy ** 2) ** 0.5
            f = 6.67408E-11 * body.m * obj.m / (r ** 2)

            body.Fx += f * dx / r
            body.Fy += f * dy / r

    def move_space_object(self, body):
        """Перемещение тела"""
        dt = self.time_step_var.get()
        ax = body.Fx / body.m
        ay = body.Fy / body.m

        body.Vx += ax * dt
        body.Vy += ay * dt
        body.x += body.Vx * dt
        body.y += body.Vy * dt

    def update_positions(self):
        #Обновление позиций на экране"""
        for body in self.space_objects:
            x = self.scale_x(body.x)
            y = self.scale_y(body.y)
            r = body.R

            if x + r < 0 or x - r > 1200 or y + r < 0 or y - r > 900:
                self.space.coords(body.image, 1200 + r, 900 + r, 1200 + 2 * r, 900 + 2 * r)
            else:
                self.space.coords(body.image, x - r, y - r, x + r, y + r)

    def scale_x(self, x):
        #Масштабирование координаты X
        return int(x * self.scale_factor) + 600

    def scale_y(self, y):
        #Масштабирование координаты Y
        return 450 - int(y * self.scale_factor)

    def start_execution(self):
        #Запуск симуляции
        self.perform_execution = True
        self.start_button.config(text="Pause", command=self.stop_execution)
        self.execution()

    def stop_execution(self):
        #Остановка симуляции
        self.perform_execution = False
        self.start_button.config(text="Start", command=self.start_execution)

    def open_file_dialog(self):
        #Загрузка системы из файла
        self.perform_execution = False
        for obj in self.space_objects:
            self.space.delete(obj.image)

        filename = filedialog.askopenfilename(filetypes=(("Text file", ".txt"),))
        if filename:
            self.load_from_file(filename)

    def load_from_file(self, filename):
        #Загрузка данных из файла
        self.space_objects = []
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

    def create_object_image(self, obj):
        #Создание графического представления объекта
        x = self.scale_x(obj.x)
        y = self.scale_y(obj.y)
        r = obj.R
        obj.image = self.space.create_oval(x - r, y - r, x + r, y + r, fill=obj.color)

    def calculate_scale(self):
        #Вычисление масштаба
        max_dist = max(max(abs(obj.x), abs(obj.y)) for obj in self.space_objects) or 1
        self.scale_factor = 0.4 * min(900, 1200) / max_dist
        print(f"Scale factor: {self.scale_factor}")


if __name__ == "__main__":
    system = SolarSystem()
    system.run()