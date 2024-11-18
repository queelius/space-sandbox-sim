from typing import Optional, Callable, Tuple
from model.body import Body
from pygame.math import Vector2 as vec2
from utils import const
import random
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


def make_line(end1: vec2, end2: vec2, mass: float, num_bodies: int) -> list[Body]:
    """
    Create a line of bodies between two endpoints, with a total mass and number of bodies.

    Parameters:
    -----------
    end1 : vec2
        The first endpoint of the line.
    end2 : vec2
        The second endpoint of the line.
    mass : float
        The total mass of the line.
    num_bodies : int
        The number of bodies in the line.
    """
    composite : list[Body] = []

    mass_per_body = mass / num_bodies
    dx = (end2.x - end1.x) / num_bodies
    dy = (end2.y - end1.y) / num_bodies

    for i in range(num_bodies):
        body = Body(pos=vec2(end1.x + i * dx, end1.y + i * dy),
                    mass=mass_per_body,
                    base_color=const.COLORS[1])
        composite.append(body)

    return composite


    

    

def make_body_square(
        layers: int,
        mass: float,
        side_length: float,
        slack: float = 1e-3,
        center: vec2 = vec2(0, 0)) -> list[Body]:
    """
    Create a bunch of bodies that form a square.

    Parameters:
    -----------
    layers : int
        The number of layers in the square.
    mass : float
        The total mass of the square.
    side_length : float
        The size length of the square.
    slack : float
        A slack factor for the distance between bodies in the outermost layer
        of the square.
    center : vec2
        The center of the square.

    Returns:
    --------
    composite : list[Body]
        A list of bodies forming the square.
    """
    x = center.x - side_length / 2
    y = center.y - side_length / 2
    composite : list[Body] = []

    # Calculate the side length such that the outermost layer of the square
    # has a side length such that the bodies are "in-contact"
    r = Body(pos=vec2(0, 0), mass=mass, base_color=(255, 0, 0)).radius
    n_outer_bodies = 4 * (side_length / r - 1)

    # create the outermost layer
    for i in range(int(n_outer_bodies)):
        body = Body(pos=vec2(x, y),
                    mass=mass / (n_outer_bodies ** 2),
                    base_color=(255, 0, 0))  # Assuming red color for visualization
        composite.append(body)
        x += r

        

    return composite


def make_body_circle(layers: int,
                     center: vec2,
                     mass: float,
                     radius: Optional[float] = None,
                     slack: float = 1e-3,
                     vel=vec2(0, 0),
                     random_color: Callable[[Body], Tuple[int, int, int]] = lambda _: (255, 0, 0)
                     ) -> list[Body]:
    """
    Create a bunch of bodies that form a circle.

    Parameters:
    -----------
    layers : int
        The number of layers in the circle.
        Note: number of bodies = 2 ** layers - 1
    center : vec2
        The center of the circle.
    mass : float
        The total mass of the circle.
    radius : float
        The radius of the circle.
        If None, we make the radius such that outermost layer of the circle
        has a radius such that the bodies are "in-contact".
    slack : float
        A slack factor for the distance between bodies in the outermost layer
        of the circle if radius is None and calculated automatically as above.
    vel : vec2
        The initial velocity of the bodies.
    random_color: Callable[[Body], Tuple[int, int, int]]
        A function that returns a random color based on the body.

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
        #print(f"Layer {layer}: {bodies_in_layer} bodies, {cur_layer_radius} layer radius")
        for i in range(bodies_in_layer):
            
            angle = i * 2 * math.pi / bodies_in_layer
            x = center.x + cur_layer_radius * math.cos(angle)
            y = center.y + cur_layer_radius * math.sin(angle)
            body = Body(pos=vec2(x, y),
                        mass=mass_per_body,
                        base_color=(255, 0, 0))
            body.base_color = random_color(body)
            body.vel = vel
            composite.append(body)
        
        cur_layer_radius += dr

    return composite





def make_shape(low_mass: float,
               high_mass: float,
               max_width: float,
               max_height: float,
               shape_pred: Callable[[vec2], bool],
               center_mass: float = None,
               slack: float = 1.5,
               max_tries = 10000) -> list[Body]:

    composite: list[Body] = []

    def is_valid(body: vec2) -> bool:
        for other in composite:
            if (body.pos - other.pos).length_squared() < (body.radius + other.radius + slack) ** 2:
                return False
        return True
    
    if center_mass is not None:
        center = Body(pos=vec2(0, 0),
                    mass=center_mass,
                    base_color=(255, 0, 0))
        if shape_pred(center.pos):
            composite.append(center)  


    while True:
        mass = low_mass
        pos = None
        tries = 0
        body = None
        while True:
            if tries > max_tries:
                return composite
            tries += 1
            x = random.uniform(-max_width / 2, max_width / 2)
            y = random.uniform(-max_height / 2, max_height / 2)
            pos = vec2(x, y)
            body = Body(pos=pos,
                        mass=mass,
                        base_color=(255, 0, 0))

            if shape_pred(pos) and is_valid(body):
                break

        while (is_valid(body)):
            body.mass += 1
            body.radius = body.mass ** (1 / 3)
            if body.mass > high_mass:
                break

        body.mass -= 1
        body.radius = body.mass ** (1 / 3)

        composite.append(body)
