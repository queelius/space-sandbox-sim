from typing import Optional, Callable
from model.body import Body
from pygame.math import Vector2 as vec2
from utils import const
from utils.utils import truncated_normal
import random
import math
from model.springs import Spring

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

def make_body_circle(layers: int,
                     center: vec2,
                     mass: float,
                     radius: Optional[float] = None,
                     slack: float = 1e-3,
                     vel=vec2(0, 0)) -> list[Body]:
    """
    Create a bunch of bodies that form a circle.

    Parameters:
    -----------
    layers : int
        The number of layers in the circle.
        Note: number of bodies = 2 ** layers - 1
    center : vec2
        The center of the circle.
    radius : float
        The radius of the circle.
        If None, we make the radius such that outermost layer of the circle
        has a radius such that the bodies are "in-contact".
    mass : float
        The total mass of the circle.
    vel : vec2
        The initial velocity of the bodies.

    Returns:
    --------
    composite : list[Body]
        A list of bodies forming the circle.
    """

    composite: list[Body] = []

    num_bodies = 2 ** layers - 1
    mass_per_body = mass / num_bodies

    if radius is None:
        # Calculate the radius such that the outermost layer of the circle
        # has a radius such that the bodies are "in-contact"        
        r = Body(pos=vec2(0, 0), mass=mass_per_body, base_color=(255, 0, 0)).radius
        n_outer_bodies = 2 ** (layers-1)
        radius = (1 + slack) * n_outer_bodies * r / math.pi
    
    # Calculate the radius increment for each layer
    dr = radius / (layers - 1)
    cur_layer_radius = 0
    for layer in range(0, layers):
        # Calculate the number of bodies in the current layer
        bodies_in_layer = 2 ** layer 
        print(f"Layer {layer}: {bodies_in_layer} bodies, {cur_layer_radius} layer radius")
        for i in range(bodies_in_layer):
            
            angle = i * 2 * math.pi / bodies_in_layer
            x = center.x + cur_layer_radius * math.cos(angle)
            y = center.y + cur_layer_radius * math.sin(angle)
            body = Body(pos=vec2(x, y),
                        mass=mass_per_body,
                        base_color=(255, 0, 0))  # Assuming red color for visualization
            body.vel = vel
            composite.append(body)
        
        cur_layer_radius += dr

    return composite





def make_shape(num_bodies: int,
               low_mass: float,
               high_mass: float,
               max_width: float,
               max_height: float,
               shape_pred: Callable[[vec2], bool],
               max_tries = None) -> list[Body]:

    if max_tries is None:
        max_tries = 100 * num_bodies
    composite: list[Body] = []

    for i in range(num_bodies):
        while max_tries > 0:
            overlap = False
            max_tries -= 1
            mass = random.uniform(low_mass, high_mass)
            x, y = None, None
            while True:
                x = random.uniform(-max_width / 2, max_width / 2)
                y = random.uniform(-max_height / 2, max_height / 2)
                pos = vec2(x, y)
                if shape_pred(pos):
                    break

            body = Body(pos=pos,
                        mass=mass,
                        base_color=(255, 0, 0))

            for other in composite:
                if (body.pos - other.pos).length_squared() < (body.radius + other.radius) ** 2:
                    overlap = True
                    break

            if not overlap:
                composite.append(body)
                break

        if max_tries == 0:
            print("Failed to create body")
            break

    return composite
