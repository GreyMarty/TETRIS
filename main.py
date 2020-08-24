import pygame as pg
from time import time
import asyncio
import numpy as np
import os

from shapes import Shape
from sound_manager import SoundManager


WINDOW_WIDTH, WINDOW_HEIGHT = 800, 900

BG_COLOR = (0, 0, 0)
LINE_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)

UI_HORIZONTAL_OFFSET = 20
UI_VERTICAL_OFFSET = -20
INFO_OFFSET = 10
UI_SCALE = 1.05

PLAYGROUND_POS = (50, 89)
GRID_SIZE = (12, 24)
CELL_SIZE = 30

FONT_SIZE = 60

pg.mixer.init()
line_effect = pg.mixer.Sound("Sounds/Line.wav")
effects_playing = []


class TetrisGame:
    def __init__(self):
        pg.init()
        pg.font.init()
        pg.display.set_caption("TETRIS")

        self.sound_manager = SoundManager()
        pg.mixer.music.load("Sounds/Music.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

        self.main_surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.playground_surf = pg.Surface((GRID_SIZE[0] * CELL_SIZE * UI_SCALE, GRID_SIZE[1] * CELL_SIZE * UI_SCALE))
        self.next_surf = pg.Surface((220 * UI_SCALE, 220 * UI_SCALE))

        self.font = pg.font.Font("Fonts/ARCADECLASSIC.TTF", int(FONT_SIZE * UI_SCALE))

        if "top.scr" in os.listdir():
            with open("top.scr") as file:
                self.top = int(file.read())
        else:
            self.top = 0

        self.score = 0
        self.lines = 0

        self.colors = np.zeros(GRID_SIZE, dtype=object)
        self.grid_colliders = np.zeros(GRID_SIZE)

        self.cur_shape = Shape(self, 5, -1)
        self.next_shape = Shape(self, 5, -1)

        self.game_over = False

    def __del__(self):
        with open("top.scr", "w") as file:
            file.write(str(self.top))

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.cur_shape.rotate()
                if event.key == pg.K_d:
                    self.cur_shape.move(1)
                if event.key == pg.K_a:
                    self.cur_shape.move(-1)

    def draw_surfaces(self):
        # Playground
        playground_pos = (
            (PLAYGROUND_POS[0] + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(self.playground_surf, playground_pos)

        # Next
        next_surf_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + UI_HORIZONTAL_OFFSET + INFO_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + GRID_SIZE[1] * CELL_SIZE - 220 + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(self.next_surf, next_surf_pos)

        self.playground_surf.fill(BG_COLOR)
        self.next_surf.fill(BG_COLOR)

    def draw_ui(self):
        # Playground
        play_rect = (
            (PLAYGROUND_POS[0] + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + UI_VERTICAL_OFFSET) * UI_SCALE,
            GRID_SIZE[0] * CELL_SIZE * UI_SCALE,
            GRID_SIZE[1] * CELL_SIZE * UI_SCALE
        )
        pg.draw.rect(self.main_surface, LINE_COLOR, play_rect, 3)

        # Top
        top_headline = self.font.render("TOP", False, TEXT_COLOR)
        top_headline_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(top_headline, top_headline_pos)
        top = self.font.render(str(self.top).zfill(6), False, TEXT_COLOR)
        top_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + 0.75 * FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(top, top_pos)

        # Score
        score_headline = self.font.render("SCORE", False, TEXT_COLOR)
        score_headline_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + 2.25 * FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(score_headline, score_headline_pos)
        score = self.font.render(str(self.score).zfill(6), False, TEXT_COLOR)
        score_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + 3 * FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(score, score_pos)

        # Lines
        lines_headline = self.font.render("LINES", False, TEXT_COLOR)
        lines_headline_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + 4.5 * FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(lines_headline, lines_headline_pos)
        lines = self.font.render(str(self.lines).zfill(6), False, TEXT_COLOR)
        lines_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + 5.25 * FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(lines, lines_pos)

        # Next
        next_headline = self.font.render("NEXT", False, TEXT_COLOR)
        next_headline_pos = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + INFO_OFFSET + UI_HORIZONTAL_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + GRID_SIZE[1] * CELL_SIZE - 220 - FONT_SIZE + UI_VERTICAL_OFFSET) * UI_SCALE
        )
        self.main_surface.blit(next_headline, next_headline_pos)
        next_rect = (
            (PLAYGROUND_POS[0] + GRID_SIZE[0] * CELL_SIZE + UI_HORIZONTAL_OFFSET + INFO_OFFSET) * UI_SCALE,
            (PLAYGROUND_POS[1] + GRID_SIZE[1] * CELL_SIZE - 220 + UI_VERTICAL_OFFSET) * UI_SCALE,
            220 * UI_SCALE,
            220 * UI_SCALE
        )
        pg.draw.rect(self.main_surface, LINE_COLOR, next_rect, 3)

    def draw_shapes(self):
        for rect_x, rect_y in self.cur_shape.get_positions():
            self.fill_cell(rect_x, rect_y, self.cur_shape.color)

        for y in range(GRID_SIZE[1]):
            for x in range(GRID_SIZE[0]):
                if self.grid_colliders[x][y]:
                    self.fill_cell(x, y, self.colors[x][y])

        # Grid
        for x in range(1, GRID_SIZE[0]):
            start_pos = x * CELL_SIZE * UI_SCALE, 0
            end_pos = x * CELL_SIZE * UI_SCALE, GRID_SIZE[1] * CELL_SIZE * UI_SCALE
            pg.draw.line(self.playground_surf, tuple(map(lambda c: int(c / 2), LINE_COLOR)), start_pos, end_pos)

        for y in range(1, GRID_SIZE[1]):
            start_pos = 0, y * CELL_SIZE * UI_SCALE
            end_pos = GRID_SIZE[0] * CELL_SIZE * UI_SCALE, y * CELL_SIZE * UI_SCALE
            pg.draw.line(self.playground_surf, tuple(map(lambda c: int(c / 2), LINE_COLOR)), start_pos, end_pos)

    def draw_next(self):
        offset_y = -0.5 if int(self.next_shape.shape[0][0]) != self.next_shape.shape[0][0] else 0
        for pos in self.next_shape.shape:
            center_x, center_y = map(lambda s: s / 2 / CELL_SIZE, self.next_surf.get_size())
            self.fill_cell(pos[0] + center_x - 0.5, pos[1] + center_y - 0.5 + offset_y, self.next_shape.color, self.next_surf)

    def fill_cell(self, x, y, color, surface=None):
        rect = (
            x * CELL_SIZE * UI_SCALE,
            y * CELL_SIZE * UI_SCALE,
            round(CELL_SIZE * UI_SCALE),
            round(CELL_SIZE * UI_SCALE)
        )

        if not surface:
            pg.draw.rect(self.playground_surf, color, rect)
        else:
            pg.draw.rect(surface, color, rect)

    def check_lines(self):
        lines = []
        for y, *line in enumerate(self.grid_colliders.T):
            if line[0].all():
                lines.append(y)

        if len(lines):
            asyncio.run(self.remove_lines(lines))

    async def remove_lines(self, lines, color=(0, 255, 0)):
        self.sound_manager.play(line_effect)
        half_bright_color = tuple(map(lambda c: int(c / 2), color))
        for i in range(5):
            for y in lines:
                if i % 2:
                    self.colors[:, y] = [color for _ in range(GRID_SIZE[0])]
                else:
                    self.colors[:, y] = [half_bright_color for _ in range(GRID_SIZE[0])]
                self.render()
            await asyncio.sleep(0.1)

        for y in lines:
            self.grid_colliders = np.delete(self.grid_colliders, y, 1)
            self.grid_colliders = np.insert(self.grid_colliders, 0, 0, 1)
            self.colors = np.delete(self.colors, y, 1)
            self.colors = np.insert(self.colors, 0, 0, 1)

            self.score += 10 * GRID_SIZE[0]
            self.top = self.score if self.score > self.top else self.top
            self.lines += 1
        self.score += (len(lines) - 1) * 25

    def logic(self, time_delta):
        if not self.game_over:
            speed_scale = 10 if pg.key.get_pressed()[pg.K_s] else 1
            self.cur_shape.update(time_delta * speed_scale)
            self.check_lines()
        else:
            self.restart()

    def restart(self):
        pg.mixer.music.rewind()
        self.score = 0
        self.lines = 0

        self.colors = np.zeros(GRID_SIZE, dtype=object)
        self.grid_colliders = np.zeros(GRID_SIZE)

        self.cur_shape = Shape(self, 5, -1)
        self.next_shape = Shape(self, 5, -1)

        self.game_over = False

    def render(self):
        self.main_surface.fill(BG_COLOR)

        self.draw_shapes()
        self.draw_next()
        self.draw_surfaces()
        self.draw_ui()

        pg.display.update()

    def mainloop(self):
        time_delta = 0
        while True:
            start = time()
            self.check_events()
            self.logic(time_delta)
            self.render()
            time_delta = time() - start


TetrisGame().mainloop()
