# controller/controller.py

import controller.states as states
from pygame.math import Vector2
from .states import dragging, idle, panning

class Controller:
    def __init__(self, event_bus, model, view):
        self.event_bus = event_bus
        self.model = model
        self.view = view
        self.selected_body = None

        # Initialize states
        self.states = {
            'idle': idle.Idle(self),
        }
        self.current_state = self.states['idle']

    def change_state(self, new_state_name):
        self.current_state.exit()
        if new_state_name not in self.states:
            if new_state_name == 'idle':
                self.states['idle'] = idle.Idle(self)
            elif new_state_name == 'dragging':
                self.states['dragging'] = dragging.Dragging(self)
            elif new_state_name == 'panning':
                self.states['panning'] = panning.Panning(self)
            else:
                raise ValueError(f"Invalid state name: {new_state_name}")
            
        self.current_state = self.states[new_state_name]        # Clean up dragging state
        self.drag_start_pos = None
        self.last_mouse_pos = None
        self.current_mouse_pos = None
        self.mouse_down_time = None

        self.current_state.enter()

    def handle_event(self, event):
        self.current_state.handle_event(event)

    def update(self):
        self.current_state.update()

    def calculate_world_pos(self, screen_pos):
        return (Vector2(screen_pos) / self.view.zoom) - self.view.pan_offset

    def is_running(self):
        return self.running
