# coding: utf-8
# license: GPLv3

class SpaceObject:
    """Базовый класс для космических объектов"""
    def __init__(self):
        self.m = 0          # масса объекта
        self.x = 0          # координата x
        self.y = 0          # координата y
        self.Vx = 0         # скорость по x
        self.Vy = 0         # скорость по y
        self.Fx = 0         # сила по x
        self.Fy = 0         # сила по y
        self.R = 5          # радиус объекта
        self.color = "red"  # цвет объекта
        self.image = None   # графическое представление
        self.parent = None  # родительский объект (для спутников)
        self.orbit = []     # точки орбиты для отрисовки
        self.type = "object"# тип объекта

class Star(SpaceObject):
    """Класс звезды"""
    def __init__(self):
        super().__init__()
        self.type = "star"
        self.color = "yellow"

class Planet(SpaceObject):
    """Класс планеты"""
    def __init__(self):
        super().__init__()
        self.type = "planet"
        self.color = "green"

class Satellite(SpaceObject):
    """Класс спутника"""
    def __init__(self):
        super().__init__()
        self.type = "satellite"
        self.color = "gray"
        self.R = 2          # спутники меньше планет