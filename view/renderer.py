import pygame
from pygame.math import Vector2 as vec2
from model.body import Body
import utils.const as const

class Renderer:
    def __init__(self, screen, width, height, bodies=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.pan_offset = vec2(0, 0)
        self.background_color = (0, 0, 0)  # Black background
        self.sel_body = None
        self.bodies = bodies

    def viewport(self):
        """
        The viewport is into the simulation space. So, it is based
        on the zoom and pan transformations.

        Returns:
        --------
        viewport : tuple
            The viewport in simulation space.
        """
        left = -self.pan_offset.x
        right = (self.width - self.pan_offset.x) / self.zoom
        top = -self.pan_offset.y
        bottom = (self.height - self.pan_offset.y) / self.zoom
        return (left, right, top, bottom)

    def render(self):
        self.screen.fill(self.background_color)
        for body in self.bodies:
            self.draw(body)

    def draw(self, body):
        # Apply zoom and pan transformations
        screen_pos = (body.pos + self.pan_offset) * self.zoom
        radius = max(1, int(body.radius * self.zoom))

        if isinstance(body, Body):
            pygame.draw.circle(self.screen,
                               body.color,
                               (int(screen_pos.x), int(screen_pos.y)),
                               radius)
            if body is self.sel_body:
                pygame.draw.circle(self.screen,
                                   const.HIGHLIGHT_COLOR,
                                   (int(screen_pos.x), int(screen_pos.y)),
                                   radius + 7, 3)
            
    def select_body(self, pos):
        # Apply zoom and pan transformations
        pos = (pos / self.zoom) - self.pan_offset
        for body in self.bodies:
            if (body.pos - pos).length_squared() < body.radius ** 2:
                self.sel_body = body
                return

    def pan(self, delta):
        self.pan_offset += delta / self.zoom

    def zoom_in(self, factor=1.1):
        self.zoom *= factor

    def zoom_out(self, factor=1.1):
        self.zoom /= factor

    def reset_view(self):
        self.zoom = 1.0
        self.pan_offset = vec2(0, 0)
