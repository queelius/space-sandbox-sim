from pygame.draw import rect
from pygame.math import Vector2 as vec2
from model.bh import Node

def draw_quads(self, screen, node: Node, zoom, pan_x, pan_y):
    """
    Draw the quadtree nodes on the screen for visualization.

    Parameters:
    -----------
    screen : pygame.Surface
        The screen to draw on.
    node : Node
        The current node to draw.
    zoom : float
        The zoom level of the screen.
    pan_x : float
        The x-panning offset.
    pan_y : float
        The y-panning offset.
    """
    if node.is_leaf():
        draw_pos = (node.center + vec2(pan_x, pan_y)) * zoom
        draw_width = node.width * zoom
        rect(screen, (255, 255, 255), (draw_pos.x - draw_width / 2,
                                                    draw_pos.y - draw_width / 2,
                                                    draw_width, draw_width), 1)
    else:
        for child in node.children:
            self.draw_quads(screen, child, zoom, pan_x, pan_y)
