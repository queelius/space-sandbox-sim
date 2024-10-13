from model.body import Body
from pygame.math import Vector2 as vec2
from utils import const
import math

def make_body_square(num_bodies_per_side, center, size, mass):
    """
    Create a bunch of bodies that form a square.

    Parameters:
    -----------
    num_bodies_per_side : int
        The number of bodies per side.
    center : vec2
        The center of the square.
    size : float
        The size of the square.
    mass : float
        The total mass of the square.

    Returns:
    --------
    composite : list[Body]
        A list of bodies forming the square.
    """
    x = center.x - size / 2
    y = center.y - size / 2
    dx = size / num_bodies_per_side
    dy = size / num_bodies_per_side
    composite : list[Body] = []
    for _ in range(num_bodies_per_side):
        for _ in range(num_bodies_per_side):
            body = Body(pos=vec2(x, y),
                        base_color=const.COLORS[1],
                        mass=mass)
            composite.append(body)
            x -= dx
        y -= dy
        x = center.x - size / 2

    return composite

def make_body_circle(num_bodies: int, center: vec2, radius: float, mass: float) -> list[Body]:
    """
    Create a bunch of bodies that form a circle.

    Parameters:
    -----------
    num_bodies : int
        The number of bodies to create.
    center : vec2
        The center of the circle.
    radius : float
        The radius of the circle.
    mass : float
        The total mass of the circle.

    Returns:
    --------
    composite : list[Body]
        A list of bodies forming the circle.
    """

    composite: list[Body] = []
    
    # Determine the number of layers (rings) we want to create
    num_layers = int(math.log2(num_bodies))
    
    # Divide the total mass equally across all bodies
    mass_per_body = mass / num_bodies
    
    # Calculate the radius increment for each layer
    dr = radius / num_layers
    
    cur_radius = dr
    for layer in range(1, num_layers + 1):
        # Calculate the number of bodies in the current layer
        bodies_in_layer = int(num_bodies / (2 ** (num_layers - layer)))
        
        for i in range(bodies_in_layer):
            angle = i * 2 * math.pi / bodies_in_layer
            x = center.x + cur_radius * math.cos(angle)
            y = center.y + cur_radius * math.sin(angle)
            body = Body(pos=vec2(x, y),
                        mass=mass_per_body,
                        base_color=(255, 0, 0))  # Assuming red color for visualization
            composite.append(body)
        
        cur_radius += dr

    return composite
