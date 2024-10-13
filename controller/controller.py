# controller/controller.py
import pygame
from pygame.math import Vector2
from model.body import Body
import random
import utils.utils as utils

class Controller:
    def __init__(self, model, view):
        self.model = model  # Reference to the BodyList
        self.view = view    # Reference to the Renderer
        self.running = True

        # State variables
        self.is_panning = False
        self.last_mouse_pos = None
        self.selected_body = None
        self.follow_selected = False

        # Event handlers
        self.event_handlers = {
            pygame.QUIT: self.handle_quit,
            pygame.MOUSEBUTTONDOWN: self.handle_mouse_button_down,
            pygame.MOUSEBUTTONUP: self.handle_mouse_button_up,
            pygame.MOUSEMOTION: self.handle_mouse_motion,
            pygame.KEYDOWN: self.handle_key_down,
            # Add more event types as needed
        }

    def handle_event(self, event):
        handler = self.event_handlers.get(event.type, None)
        if handler:
            handler(event)
            # Else, ignore the event or handle it in a default way

    # Event handler methods
    def handle_quit(self, event):
        self.running = False

    def handle_mouse_button_down(self, event):
        if event.button == 1:  # Left click
            self.handle_left_click(event)
        elif event.button == 2:  # Middle click
            self.start_panning(event)
        elif event.button == 4:  # Scroll up
            self.view.zoom_in()
        elif event.button == 5:  # Scroll down
            self.view.zoom_out()

    def handle_mouse_button_up(self, event):
        if event.button == 2:  # Middle click
            self.stop_panning(event)

    def handle_mouse_motion(self, event):
        if self.is_panning:
            self.pan_view(event)

    def handle_key_down(self, event):
        if event.key == pygame.K_a:  # 'a' key to add an orbital body
            self.add_orbital_body()
        # Add more key handlers as needed

    # Helper methods
    def handle_left_click(self, event):
        mouse_pos = Vector2(event.pos)
        world_pos = (mouse_pos / self.view.zoom) - self.view.pan_offset

        # Check if a body was clicked
        for body in self.model:
            if (body.pos - world_pos).length_squared() <= body.radius ** 2:
                self.selected_body = body
                self.follow_selected = True
                print(f"Selected body: {body}")
                return

        # If no body was clicked, create a new body
        self.create_new_body(world_pos)

    def start_panning(self, event):
        self.is_panning = True
        self.last_mouse_pos = Vector2(event.pos)

    def stop_panning(self, event):
        self.is_panning = False

    def pan_view(self, event):
        current_mouse_pos = Vector2(event.pos)
        delta = current_mouse_pos - self.last_mouse_pos
        self.view.pan(delta)
        self.last_mouse_pos = current_mouse_pos

    def create_new_body(self, pos):
        # Implement logic to create a new body at the given pos
        # For simplicity, we'll create a body with default parameters
        new_body = Body(
            pos=pos,
            mass=5e2,
            base_color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        )
        self.model.add(new_body)
        print(f"Created new body at {pos}")

    def add_orbital_body(self):
        if self.selected_body is None:
            print("No body selected to orbit around.")
            return
        
        orbit_distance = self.selected_body.radius * 1.1
        angle = random.uniform(0, 2 * 3.1415926)
        pos = self.selected_body.pos + Vector2(orbit_distance, 0).rotate_rad(angle)

        utils.add_orbital_body(bodies=self.model,
                               other_body=self.selected_body,
                               pos=pos,
                               mass=5e2,
                               eccentricity=0)
        print(f"Added orbital body around {self.selected_body}")

    def is_running(self):
        return self.running
