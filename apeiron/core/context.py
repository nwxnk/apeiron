# coding: utf-8

import pygame

from . import trans
from .state import State, StateManager

def call_func(obj, name, *a, **k):
    if obj:
        return getattr(obj, name, lambda *a, **k: None)(*a, **k)

class ContextBuilder:
    def __init__(self, title, width, height):
        self.config = {
            'fps'       : 0,
            'icon'      : None,
            'show_mouse': True,
            'title'     : title,
            'vsync'     : False,
            'resizable' : False,
            'fullscreen': False,
            'grab_mouse': False,
            'size'      : (width, height)}

    def __str__(self):
        return str(self.config)

    def __getattr__(self, name): # poggers?
        if name in self.config.keys():
            return lambda d: self.config.update({name: d}) or self

    def build(self):
        return Context(**self.config)

class Context:
    def __init__(self, **config):
        self.config = config
        self.configure_ctx()

        self.state_manager = StateManager()

    def configure_ctx(self):
        pygame.init()

        pygame.event.set_grab(self.config['grab_mouse'])
        pygame.mouse.set_visible(self.config['show_mouse'])
        pygame.display.set_caption(self.config['title'])

        self.clock  = pygame.time.Clock()
        self.flags  = pygame.RESIZABLE  *  self.config['resizable'] | \
                      pygame.FULLSCREEN * self.config['fullscreen']
        self.screen = pygame.display.set_mode(self.config['size'], self.flags)

        if self.config['icon']:
            pygame.display.set_icon(self.config['icon'])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                while self.state_manager.state:
                    self.state_manager.pop()

                exit(pygame.quit() or 0)

            event_name = pygame.event.event_name(event.type).lower()
            transition = call_func(self.state_manager.state, f'handle_{event_name}_event', event)
 
            if transition:
                {
                    'POP' : lambda state: self.state_manager.pop(),
                    'SET' : lambda state: self.state_manager.set(state(self)),
                    'PUSH': lambda state: self.state_manager.push(state(self))
                }.get(transition.trans, lambda s: None)(transition.state)

    def run(self, initial_state):
        self.state_manager.push(initial_state(self))

        while self.state_manager.state:
            self.handle_events()
            call_func(self.state_manager.state, 'draw')
            call_func(self.state_manager.state, 'update')
            self.clock.tick(self.config['fps'])
            pygame.display.flip()

        exit(pygame.quit() or 0)