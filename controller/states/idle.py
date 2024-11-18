import pygame

class Idle:
    def __init__(self, controller):
        self.controller = controller

        self.params = {
            "new_body_mass": 1e3,
            "new_body_radius": None,
            "new_body_color": None,
            "new_body_velocity": pygame.Vector2(0, 0),
            "zoom_in_factor": 1.05,
            "zoom_out_factor": 1.05,
        }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down(event)
        elif event.type == pygame.KEYUP:
            self.handle_key_up(event)
        elif event.type == pygame.QUIT:
            self.controller.event_bus.publish('exit', {})

    def handle_mouse_button_down(self, event):
        if event.button == 1:  # Left click
            self.handle_left_click(event)
        elif event.button == 2:  # Middle click
            self.controller.change_state('panning')
        elif event.button == 4:  # Scroll up
            self.controller.event_bus.publish('zoom_in', {"factor": 1.05})
        elif event.button == 5:  # Scroll down
            self.controller.event_bus.publish('zoom_out', {"factor": 1.05})

    def handle_left_click(self, event):
        # Check if a body was clicked
        body = self.get_body_at_mouse(event.pos)
        if body:
            if self.controller.selected_body is not None:
                if body is not self.controller.selected_body:
                    self.controller.event_bus.publish("unselect_body", {"body": self.controller.selected_body})
                    self.controller.event_bus.publish("select_body", {"body": body})
                self.controller.change_state('dragging')
            else:
                self.controller.event_bus.publish('select_body', {'body': body})
                self.controller.change_state('dragging')
        else:
            self.controller.event_bus.publish('new_body', {'position': self.controller.calculate_world_pos(event.pos)})

    def handle_key_up(self, event):
        # self.controller.event_bus.publish("key_up_event", {
        #     "key": event.key,
        #     "controller_state": str(self),
        #     "event": event,
        #     "modifier": pygame.key.get_mods()
        # })

        if event.key == pygame.K_a:
            self.controller.event_bus.publish('add_orbital_bodies',
                                              { "num_bodies": 1,
                                                "mass": 1e3,
                                                "radius": None,
                                                "color": None,
                                                "theta": None,
                                                "r": None,
                                                "body_orbiting": self.controller.selected_body })                                                                      })
        elif event.key == pygame.K_PAUSE:
            self.controller.event_bus.publish('toggle_pause', {})
        elif event.key == pygame.K_w:
            self.controller.event_bus.publish("add_rotational_energy", {"energy": 1e5})
        elif event.key == pygame.K_r:
            self.controller.event_bus.publish('clear_bodies', {})
        elif event.key == pygame.K_q:
            self.controller.event_bus.publish('exit', {})
        elif event.key == pygame.K_TAB:
            if self.controller.selected_body is None:
                self.controller.event_bus.publish("select_body", {"body": self.controller.model[0]})
            else:
                next_body_index = self.controller.model.index(self.controller.selected_body) + 1
                if next_body_index >= len(self.controller.model):
                    next_body_index = 0
                self.controller.event_bus.publish("select_body", {"body": self.controller.model[next_body_index]})
        elif event.key == pygame.K_u:
            self.controller.event_bus.publish("unselect_body", { "body": self.controller.selected_body })
        elif event.key == pygame.K_DELETE:
            if self.controller.selected_body is not None:
                body = self.controller.selected_body
                self.controller.event_bus.publish("unselect_body", {"body": body})
                self.controller.event_bus.publish("delete_body", {"body": body})
                

    def get_body_at_mouse(self, mouse_pos):
        world_pos = self.controller.calculate_world_pos(mouse_pos)
        for body in self.controller.model:
            if (body.pos - world_pos).length_squared() <= body.radius ** 2:
                return body
        return None
    
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass


