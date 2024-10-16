import pygame
from pygame.draw import rect
from model.bh import Node

def draw_hull(hull, screen, zoom, pan_offset) -> None:
    """
    Draw the convex hull on the screen.
    """
    for i in range(len(hull)):
        start_pos = (hull[i] + pan_offset) * zoom
        end_pos = (hull[(i + 1) % len(hull)] + pan_offset) * zoom
        pygame.draw.line(surface=screen,
                        color=(255, 255, 255),
                        start_pos=(int(start_pos.x), int(start_pos.y)),
                        end_pos=(int(end_pos.x), int(end_pos.y)),
                        width=10)


def draw_quads(node: Node, screen, zoom, pan_offset) -> None:
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
        draw_pos = (node.center + pan_offset) * zoom
        draw_width = node.width * zoom
        rect(screen, (255, 255, 255), (draw_pos.x - draw_width / 2,
                                                    draw_pos.y - draw_width / 2,
                                                    draw_width, draw_width), 1)
    else:
        for child in node.children:
            draw_quads(screen, child, zoom, pan_offset)

def draw_springs(springs, screen, zoom, pan_offset) -> None:
    """
    Draw the springs on the screen for visualization.
    """
    for spring in springs:
        body1, body2, _, _, _, _ = spring
        start = (body1.pos + pan_offset) * zoom
        end = (body2.pos + pan_offset) * zoom
        pygame.draw.line(screen, (255, 255, 255), start, end, 2)
