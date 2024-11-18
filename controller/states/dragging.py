import pygame
from pygame.math import Vector2
from collections import deque
import numpy as np

class Dragging:
    def __init__(self, controller):
        self.controller = controller
        self.drag_start_pos = None
        self.last_mouse_pos = None
        self.current_mouse_pos = None
        self.mouse_down_time = None
        self.mouse_positions = deque(maxlen=10)  # Use a deque to store the last 5 positions for velocity calculation
        self.mouse_times = deque(maxlen=10)  # Store corresponding timestamps

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.handle_left_release(event)
        elif event.type == pygame.QUIT:
            self.controller.publish('exit', {})

    def handle_mouse_motion(self, event):
        self.last_mouse_pos = self.current_mouse_pos
        self.current_mouse_pos = Vector2(event.pos)
        current_time = pygame.time.get_ticks()

        if self.drag_start_pos is None:
            self.drag_start_pos = self.current_mouse_pos
            self.mouse_down_time = current_time
        
        # Add the current position and time to the deques
        self.mouse_positions.append(self.current_mouse_pos)
        self.mouse_times.append(current_time)

        # Publish an event to move the body
        world_pos = self.controller.calculate_world_pos(self.current_mouse_pos)
        self.controller.event_bus.publish('body_moved', {
            'body': self.controller.selected_body,
            'new_pos': world_pos,
            'new_vel': Vector2(0, 0)
        })

    def handle_left_release(self, event):
        # Determine if it was a click or a drag
        mouse_up_time = pygame.time.get_ticks()
        time_held = (mouse_up_time - self.mouse_down_time) / 1000.0  # seconds

        #self.mouse_positions.append(self.current_mouse_pos)
        #self.mouse_times.append(mouse_up_time)

        if time_held > 0.1 and len(self.mouse_positions) > 1:
            # Use linear regression to estimate velocity
            positions = np.array([pos.xy for pos in self.mouse_positions])
            times = np.array(self.mouse_times) / 1000.0  # Convert to seconds
            times -= times[0]  # Normalize time to start at 0

            # Perform linear regression separately for x and y
            A = np.vstack([times, np.ones(len(times))]).T
            vx, _ = np.linalg.lstsq(A, positions[:, 0], rcond=None)[0]
            vy, _ = np.linalg.lstsq(A, positions[:, 1], rcond=None)[0]
            velocity = Vector2(vx, vy)

            world_pos = self.controller.calculate_world_pos(self.current_mouse_pos)            
            self.controller.event_bus.publish("body_moved", {
                "body": self.controller.selected_body,
                'new_vel': 0.4 * velocity,
                'new_pos': world_pos
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
        self.mouse_positions.clear()
        self.mouse_times.clear()

    def update(self):
        self.controller.event_bus.publish('body_moved', {
            'body': self.controller.selected_body,
            'new_vel': Vector2(0, 0)
        })
