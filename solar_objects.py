# coding: utf-8
# license: GPLv3

class Star:
    type = "star"
    def __init__(self):
        self.m = 0
        self.x = 0
        self.y = 0
        self.Vx = 0
        self.Vy = 0
        self.Fx = 0
        self.Fy = 0
        self.R = 5
        self.color = "red"
        self.image = None

class Planet:
    type = "planet"
    def __init__(self):
        self.m = 0
        self.x = 0
        self.y = 0
        self.Vx = 0
        self.Vy = 0
        self.Fx = 0
        self.Fy = 0
        self.R = 5
        self.color = "green"
        self.image = None