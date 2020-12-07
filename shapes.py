import pygame as pg
from pygame.math import Vector2
from math import floor, sin, cos, pi
from random import choice
import numpy as np


shapes = [
    ((0.5, 0.5), (1.5, 0.5), (-0.5, 0.5), (-1.5, 0.5)),  # line
    ((0, 0), (1, 0), (-1, 0), (-1, -1)),  # l-shape
    ((0, 0), (1, 0), (1, -1), (-1, 0)),  # l-shape reversed
    ((0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)),  # rect
    ((0, 0), (1, 0), (0, -1), (-1, -1)),  # z-shape
    ((0, 0), (0, -1), (1, -1), (-1, 0)),  # z-shape reversed
    ((0, 0), (0, -1), (1, 0), (-1, 0))  # t-shape
]

palette = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255)
]

pg.mixer.init()
move_effect = pg.mixer.Sound("Sounds/Move.wav")
land_effect = pg.mixer.Sound("Sounds/Land.wav")
rotate_effect = pg.mixer.Sound("Sounds/Rotate.wav")


class Shape:
    def __init__(self, main, x, y, speed_scale=1):
        self.center = Vector2(x, y)
        self.shape = np.array(choice(shapes))
        self.color = choice(palette)
        self.main = main

        self.pos_y_float = 0
        self.falling_speed = 3 * speed_scale

    def get_positions(self):
        for pos in self.shape:
            if int(pos[0]) != pos[0]:
                yield int(self.center.x + pos[0] + 0.5), int(self.center.y - pos[1] + 0.5)
            else:
                yield int(self.center.x + pos[0]), int(self.center.y + pos[1])

    def update(self, time_delta):
        self.pos_y_float += self.falling_speed * time_delta
        if self.pos_y_float > 1:
            if self.is_colliding():
                self.land()

            self.pos_y_float -= floor(self.pos_y_float)
            self.center.y += 1

    def is_colliding(self, axis="y"):
        for pos in self.get_positions():
            try:
                if axis == "y":
                    if pos[1] + 1 >= 0 and self.main.grid_colliders[pos[0]][pos[1]+1]:
                        return True
                if axis == "x":
                    if self.main.grid_colliders[pos[0]][pos[1]] or pos[0] < 0:
                        return True
            except IndexError:
                return True

        return False

    def land(self):
        self.main.sound_manager.play(land_effect)
        for x, y in self.get_positions():
            if y == 0:
                self.main.game_over = True
                print("game over")
                return
            self.main.grid_colliders[x][y] = 1
            self.main.colors[x][y] = self.color

        self.main.cur_shape = self.main.next_shape
        self.main.next_shape = Shape(self.main, 5, -1)

    def rotate(self):
        """
        x = r * cos(a + d)
        x = r * cos(a) * cos(d) - r * sin(a) * sin(d)
        x = x * cos(d) - y * sin(d)

        y = r * sin(a + d)
        y = r * sin(a) * cos(d) + r * cos(a) * sin(d)
        y = y * cos(d) + x * sin(d)
        """

        self.main.sound_manager.play(rotate_effect)
        shape = self.shape.copy()

        for ind, (x, y) in enumerate(self.shape):
            new_x = x * int(cos(pi / 2)) - y * int(sin(pi / 2))
            new_y = y * int(cos(pi / 2)) + x * int(sin(pi / 2))

            try:
                pos = self.center + Vector2(new_x, new_y)
                pos += Vector2(0.5, 0.5) if int(pos.x) != pos.x else Vector2(0, 0)
                if pos.x < 0 or pos.y < 0 or self.main.grid_colliders[int(pos.x)][int(pos.y)]:
                    self.shape = shape
                    return
            except IndexError:
                self.shape = shape
                return

            self.shape[ind] = new_x, new_y

    def move(self, direction):
        self.main.sound_manager.play(move_effect)
        self.center.x += direction
        if self.is_colliding(axis="x"):
            self.center.x -= direction
