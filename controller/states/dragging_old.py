import pygame
from pygame.math import Vector2

class Dragging:
    def __init__(self, controller):
        self.controller = controller
        self.drag_start_pos = None
        self.last_mouse_pos = None
        self.current_mouse_pos = None
        self.mouse_down_time = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.handle_left_release(event)
        elif event.type == pygame.KEYUP:
            self.handle_key_up(event)
        elif event.type == pygame.QUIT:
            self.controller.running = False

    def handle_mouse_motion(self, event):
        self.last_mouse_pos = self.current_mouse_pos
        self.current_mouse_pos = Vector2(event.pos)
        if self.drag_start_pos is None:
            self.drag_start_pos = self.current_mouse_pos
            self.mouse_down_time = pygame.time.get_ticks()
        # Publish an event to move the body
        world_pos = self.controller.calculate_world_pos(self.current_mouse_pos)
        self.controller.event_bus.publish('body_moved', {
            'body': self.controller.selected_body,
            'new_pos': world_pos
        })

    def handle_left_release(self, event):
        # Determine if it was a click or a drag
        mouse_up_time = pygame.time.get_ticks()
        time_held = (mouse_up_time - self.mouse_down_time) / 1000.0  # seconds

        if time_held > 0.1 and self.last_mouse_pos is not None:
            cur_world_pos = self.controller.calculate_world_pos(self.current_mouse_pos)
            last_world_pos = self.controller.calculate_world_pos(self.last_mouse_pos)
            velocity = (cur_world_pos - last_world_pos) / time_held
            self.controller.event_bus.publish("fling_body", {
                "body": self.controller.selected_body,
                "velocity": velocity
            })

        self.controller.change_state('idle')

    def enter(self):
        self.mouse_down_time = pygame.time.get_ticks()

    def exit(self):
        # Clean up dragging state
        self.drag_start_pos = None
        self.last_mouse_pos = None
        self.current_mouse_pos = None
        self.mouse_down_time = None

    def update(self):
        pass
