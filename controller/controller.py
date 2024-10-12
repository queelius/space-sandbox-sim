# controller/controller.py
import pygame
from pygame.math import Vector2

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

    def handle_events(self):
        for event in pygame.event.get():
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
            if (body.position - world_pos).length_squared() <= body.radius ** 2:
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

    def create_new_body(self, position):
        # Implement logic to create a new body at the given position
        # For simplicity, we'll create a body with default parameters
        from model.body import Body
        import random
        new_body = Body(
            position=position,
            mass=1e10,
            color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        )
        self.model.add(new_body)
        print(f"Created new body at {position}")

    def add_orbital_body(self):
        if self.selected_body is None:
            print("No body selected to orbit around.")
            return

        # For simplicity, we'll create a body at a fixed distance
        from model.body import Body
        import random
        orbit_distance = self.selected_body.radius * 5
        angle = random.uniform(0, 2 * 3.1415926)
        position = self.selected_body.position + Vector2(orbit_distance, 0).rotate_rad(angle)

        # Calculate orbital velocity
        G = 6.67430e-11  # Gravitational constant
        mass = self.selected_body.mass * 0.01  # 1% of the selected body's mass
        orbital_speed = (G * self.selected_body.mass / orbit_distance) ** 0.5
        velocity_direction = (position - self.selected_body.position).rotate(90).normalize()
        velocity = velocity_direction * orbital_speed

        new_body = Body(
            position=position,
            mass=mass,
            color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        )
        new_body.velocity = self.selected_body.velocity + velocity
        self.model.add(new_body)
        print(f"Added orbital body around {self.selected_body}")

    def is_running(self):
        return self.running
