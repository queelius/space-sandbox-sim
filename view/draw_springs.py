import pygame

def draw_springs(screen, springs, zoom, pan_x, pan_y) -> None:
    for spring in springs:
        body1, body2, _, _, _, _ = spring
        start = (body1.pos + (pan_x, pan_y)) * zoom
        end = (body2.pos + (pan_x, pan_y)) * zoom
        pygame.draw.line(screen, (255, 255, 255), start, end, 1)

