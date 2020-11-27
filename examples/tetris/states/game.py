# coding: utf-8

from tetris import states
from tetris.logic import Shape
from tetris.logic import Board

from threading import Timer
from apeiron import (
    draw, trans,
    pygame, State)

import pygame.freetype

kevent = (pygame.event.custom_type(), 1000 // 15) #   key event
bevent = (pygame.event.custom_type(), 1000 // 5 ) # board event

colors = [
    (  0,   0, 255),
    (  0, 150,   0),
    (255,   0,   0),
    (255, 120,   0),
    (255, 255,   0),
    (  0, 220, 220),
    (180,   0, 255)]

class Game(State):
    def on_start(self):
        pygame.freetype.init()
        pygame.time.set_timer(*bevent)

        self.block = pygame.Rect(200, 20, 20, 20)
        self.ctx.board = Board()
        self.ctx.mfont = pygame.freetype.SysFont('monospace', 13)

    def on_stop(self):
        pygame.time.set_timer(kevent[0], 0)
        pygame.time.set_timer(bevent[0], 0)

    def on_pause(self):
        self.on_stop()

    def on_resume(self):
        pygame.time.set_timer(*bevent)

    def handle_quit_event(self, event):
        pygame.quit(); exit(0)

    def handle_bevent_event(self, event): # called by on_userevent_event
        if self.ctx.board.is_game_finished:
            return trans.POP()

        self.ctx.board.one_line_down()

    def handle_kevent_event(self, event): # called by on_userevent_event
        shape = self.ctx.board.shape
        pkeys = pygame.key.get_pressed()

        dx, dy = {
            pkeys[pygame.K_DOWN ]: ( 0, 1),
            pkeys[pygame.K_LEFT ]: (-1, 0),
            pkeys[pygame.K_RIGHT]: ( 1, 0)
        }.get(1, (0, 0))

        self.ctx.board.move(shape, shape.x + dx, shape.y + dy)

    def handle_userevent_event(self, event):
        func = {
            bevent[0]: self.handle_bevent_event,
            kevent[0]: self.handle_kevent_event
        }.get(event.type, lambda *a, **k: None)

        return func(event)

    def handle_keyup_event(self, event):
        if event.key in [pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            pygame.time.set_timer(kevent[0], 0)

    def handle_keydown_event(self, event):
        shape = self.ctx.board.shape

        if event.key == pygame.K_SPACE:
            self.ctx.board.hard_drop()

        elif event.key in [pygame.K_z, pygame.K_x, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            shape, dx, dy = {
                pygame.K_z    : (shape.rotate( 1),  0, 0),
                pygame.K_x    : (shape.rotate(-1),  0, 0),
                pygame.K_DOWN : (           shape,  0, 1),
                pygame.K_LEFT : (           shape, -1, 0),
                pygame.K_RIGHT: (           shape,  1, 0)
            }.get(event.key)

            self.ctx.board.move(shape, shape.x + dx, shape.y + dy)

            if event.key not in [pygame.K_z, pygame.K_x]:
                Timer(5 / kevent[1], pygame.time.set_timer, kevent).start()

    def draw_next_shape(self):
        pass

    def draw_score(self):
        draw.rect(self.ctx, (0, 0, 0), (430, 20, 140, 30), 3)
        self.ctx.mfont.render_to(
            self.ctx.screen, (465, 31),
            f'Score: {self.ctx.board.score}', (0, 0, 0))

    def draw_board(self):
        for (x, y) in self.ctx.board.shape.coords:
            draw.rect(
                self.ctx,
                colors[self.ctx.board.shape.shape],
                self.block.move(
                    (x + self.ctx.board.shape.x) * self.block.width,
                    (y + self.ctx.board.shape.y) * self.block.height))

        for y in range(self.ctx.board.BOARD_H):
            for x in range(self.ctx.board.BOARD_W):
                if (shape := self.ctx.board.get_shape(x, y)) is not None:
                    draw.rect(
                        self.ctx,
                        colors[shape],
                        self.block.move(x * self.block.width, y * self.block.height))

                draw.rect(
                    self.ctx,
                    (202, 202, 202),
                    self.block.move(x * self.block.width, y * self.block.height), 1)

        draw.rect(self.ctx, (0, 0, 0), (200, 20, 200, 480), 3)

    def draw(self):
        draw.clear(self.ctx, (238, 238, 238))

        self.draw_board()
        self.draw_score()
        self.draw_next_shape()