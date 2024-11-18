import pygame
from pygame.draw import rect
from model.bh import Node
from pygame.math import Vector2 as vec2
from model.body import Body
from utils import const

def draw_body(body: Body,
              highlight: bool,
              screen: pygame.Surface,
              zoom: float,
              pan_offset: vec2,
              color: tuple[int, int, int] = None,
              highlight_color: tuple[int, int, int] = const.HIGHLIGHT_COLOR,
              min_radius: float = 1,
              highlight_margin: float = 7,
              highlight_width: float = 3) -> None:
    
    if color is None:
        color = body.color

    screen_pos = (body.pos + pan_offset) * zoom
    radius = int(max(min_radius, body.radius * zoom))

    pygame.draw.circle(screen,
                       body.color,
                       (int(screen_pos.x), int(screen_pos.y)),
                       radius)
    
    if highlight:
        pygame.draw.circle(screen, highlight_color,
                           (int(screen_pos.x), int(screen_pos.y)),
                           radius + highlight_margin, highlight_width)


def draw_hull(hull: list[vec2],
              renderer,
              color: tuple[int, int, int] = (200, 200, 200),
              fill: bool = False) -> None:
    """
    Draw the convex hull on the screen.

    Parameters:
    -----------
    hull : list of vec2
        The hull to draw.
    renderer : Renderer
        The renderer to draw on. It is in this case a wrapper for a
        pygame.Surface object and other rendering parameters.
    color : tuple[int, int, int], optional
        The color of the hull (default is white).
    fill : bool, optional
        Whether to fill the hull or not (default is False).
    """

    if not hull:
        return

    scr, zoom, pan = renderer.screen, renderer.zoom, renderer.pan_offset    
    if fill:
        if len(hull) < 3:
            return
        
        # Prepare the points for the filled polygon
        points = [
            (int((point + pan).x * zoom),
             int((point + pan).y * zoom))
            for point in hull
        ]
        pygame.draw.polygon(
            surface=scr,
            color=color,
            points=points
        )
    else:
        # Draw the hull edges as lines
        for i in range(len(hull)):
            start = (hull[i] + pan) * zoom
            end = (hull[(i + 1) % len(hull)] + pan) * zoom
            pygame.draw.line(
                surface=scr,
                color=color,
                start_pos=(int(start.x), int(start.y)),
                end_pos=(int(end.x), int(end.y)),
                width=4
            )


def draw_quadtree(node: Node,
                  renderer,
                  color: tuple[int, int, int] = (150, 150, 150)) -> None:
    """
    Draw the quadtree nodes on the screen for visualization.

    Parameters:
    -----------
    node : Node
        The current node to draw.
    renderer : Renderer
        The renderer to draw on. It is in this case, it wraps pygame.Surface
        object and other rendering parameters.
    color : tuple[int, int, int], optional
        The color of the quadtree nodes (default is light gray).
    """
    if node is None:
        return
    
    scr, zoom, pan = renderer.screen, renderer.zoom, renderer.pan_offset
    if node.is_leaf():
        draw_pos = (node.center + pan) * zoom
        draw_width = node.width * zoom
        rect(scr, color, (draw_pos.x - draw_width / 2,
                          draw_pos.y - draw_width / 2,
                          draw_width, draw_width), 1)
    else:
        for child in node.children:
            draw_quadtree(child, scr, zoom, pan)

def draw_springs(springs,
                 renderer,
                 color: tuple[int, int, int] = (200, 200, 200)) -> None:
    """
    Draw the springs on the screen for visualization.

    Parameters:
    -----------
    springs : list
        The springs to draw.
    renderer : Renderer
        The renderer to draw on. It is in this case a pygame.Surface object.
    """
    scr, zoom, pan = renderer.screen, renderer.zoom, renderer.pan_offset
    for spring in springs:
        body1, body2, _, _, _, _, _ = spring
        start = (body1.pos + pan) * zoom
        end = (body2.pos + pan) * zoom
        
        pygame.draw.line(scr, color, start, end, 2)

