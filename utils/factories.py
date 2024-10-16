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

def make_body_circle(num_bodies: int,
                     center: vec2,
                     radius: float,
                     mass: float,
                     vel=vec2(0, 0)) -> list[Body]:
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
    vel : vec2
        The initial velocity of the bodies.

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
            body.vel = vel
            composite.append(body)
        
        cur_radius += dr

    return composite

def make_circle(num_bodies: int,
                expected_total_mass: float,
                com: vec2,                           
                com_vel: vec2,
                radius: float,                            
                core_mass_prop: Optional[float],
                max_tries = None) -> list[Body]:
    """
    Create a bunch of bodies that form a circle.

    Parameters:
    -----------
    num_bodies : int
        The number of bodies to create.
    expected_total_mass : float
        The expected total mass of the circle.
    com : vec2
        The center of mass of the circle.
    com_vel : vec2
        The velocity of the center of mass.
    radius : float
        The radius of the composite circle.
    core_mass_frac : float
        The fraction of mass that should be concentrated in a core at the
        center of mass of the circle. If None, no core is created.
    
    Returns:
    --------
    composite : list[Body]
        A list of bodies forming the circle.
    """

    if max_tries is None:
        max_tries = 10000 * num_bodies
    composite: list[Body] = []
    if core_mass_prop is not None:
        mass_core = expected_total_mass * core_mass_prop
        expected_total_mass -= mass_core
        core = Body(pos=com,
                    mass=mass_core,
                    base_color=(255, 0, 0))
        core.vel = com_vel
        num_bodies -= 1
        composite.append(core)
        range_min = core.radius
        range_max = radius
    else:
        range_min = 0
        range_max = radius

    body_mass_mu = expected_total_mass / num_bodies
    for i in range(num_bodies):
        print(f"Creating body {i}")
        overlap = False
        while max_tries > 0:
            max_tries -= 1
            mass = truncated_normal(
                mu=body_mass_mu,
                sigma=0.1 * body_mass_mu,
                lower=0.05 * body_mass_mu)
            #print(f"mass: {mass}")
            
            d = truncated_normal(mu=0,
                                 sigma=radius,
                                 lower=range_min,
                                 upper=range_max)
            #print(f"d: {d}")
            theta = random.uniform(0, 2 * math.pi)
            x = com.x + d * math.cos(theta)
            y = com.y + d * math.sin(theta)
            #print(f"x: {x}, y: {y}")
            body = Body(pos=vec2(x, y),
                        mass=mass,
                        base_color=(255, 0, 0))
            
            #print(f"body: {body}")

            # check for overlap with existing bodies
            if len(composite) == 0:
                overlap = False
                
            for other in composite:
                #print(f"Checking overlap for {body} and {other}")
                if (body.pos - other.pos).length_squared() < 0.25 * (body.radius + other.radius) ** 2:
                    #print("Overlap")
                    overlap = True
                    break

            if not overlap:
                body.vel = com_vel
                composite.append(body)
                break

        


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
