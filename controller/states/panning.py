import pygame
from pygame.math import Vector2

class Panning:
    def __init__(self, controller):
        self.controller = controller
        self.last_mouse_pos = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:  # Middle mouse button release
                self.handle_middle_release(event)
        elif event.type == pygame.QUIT:
            self.controller.event_bus.publish('quit')

    def handle_mouse_motion(self, event):
        current_mouse_pos = Vector2(event.pos)
        if self.last_mouse_pos is not None:
            delta = current_mouse_pos - self.last_mouse_pos
            self.controller.event_bus.publish('pan_view', {'delta': delta})
        self.last_mouse_pos = current_mouse_pos

    def handle_middle_release(self, event):
        self.controller.change_state('idle')

    def enter(self):
        pass

    def exit(self):
        self.last_mouse_pos = None

    def update(self):
        pass
