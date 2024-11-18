# view/renderer.py
from pygame.math import Vector2 as vec2
from pygame import Surface
from model.body import Body
from model.body_list import BodyList
from events.event_bus import EventBus
import view.draw as draw

class Renderer:
    def __init__(self,
                 event_bus: EventBus,
                 screen: Surface,
                 width: int,
                 height: int,
                 bodies: BodyList):
        self.event_bus = event_bus
        self.screen = screen
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.pan_offset = vec2(0, 0)
        self.background_color = (0, 0, 0)  # Black background
        self.selected_body = None
        self.bodies = bodies
        self.draw_bodies = True
        self.draw_quadtree = False
        self.root = None

        event_bus.subscribe("select_body", self.handle_select_body)

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

        if self.draw_bodies:
            for body in self.bodies:
                draw.draw_body(
                    body=body,
                    highlight=body is self.selected_body,
                    screen=self.screen,
                    zoom=self.zoom,
                    pan_offset=self.pan_offset)
                
    def pan(self, delta):
        self.pan_offset += delta / self.zoom

    def zoom_in(self, factor=1.1):
        self.zoom *= factor
    
    def zoom_out(self, factor=1.1):
        self.zoom /= factor

    def handle_select_body(self, data):
        self.selected_body = data.get("select_body", None)

    def reset_view(self):
        self.zoom = 1.0
        self.pan_offset = vec2(0, 0)
