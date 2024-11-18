import math
from scipy.stats import truncnorm
from pygame.math import Vector2 as vec2
from typing import Optional
import random
import utils.const as const
from model.body import Body
from model.body_list import BodyList

def distance(p1 : vec2, p2 : vec2) -> float:
    """
    Calculate the Euclidean distance between two points.
    """
    return (p1 - p2).length()

def distance2(p1 : vec2, p2 : vec2) -> float:
    """
    Calculate the Euclidean distance between two points.
    """
    return (p1 - p2).length_squared()

def generate_orbital_bodies(
        num_bodies : int,
        orbit_around : Body,
        dist_truncnorm: tuple[float, float, float, float],
        relative_mass_truncnorm: tuple[float, float, float, float],
        radius_truncnorm: Optional[tuple[float, float, float, float]] = None,
        density_truncnorm: Optional[tuple[float, float, float, float]] = None,
        eccentricity_truncnorm: tuple[float, float, float, float] = (0, 1, 0, 0),
        G: float = const.SIM_GRAVITY) -> list[Body]:
    """
    Generate orbital bodies around an `orbit_around`. This assumes
    that the relative mass of the new bodies is negligible compared
    to the mass of the `orbit_around`, so that the new bodies will
    not affect the orbit of the `orbit_around` significantly.

    Notes: This function has a complicated signature because it allows
    for a lot of customization, but the default values are set to allow
    for simple usage. Either `radius_truncnorm` or `density_truncnorm`
    should be specified, but not both. If neither is specified, the
    radius will be determined by the mass with some default density
    assumption.

    Parameters:
    -----------
    num_bodies : int
        The number of bodies to generate.
    orbit_around : Body
        The body around which the new bodies will orbit.
    dist_truncnorm : tuple[float, float, float, float]
        The parameters for the truncated normal distribution of the
        distance from the `orbit_around` body. The tuple should be
        in the form (min, max, mu, sd).
    relative_mass_truncnorm : tuple[float, float, float, float]
        The parameters for the truncated normal distribution of the
        relative mass of the new bodies. The tuple should be in the
        form (min, max, mu, sd).
    density_truncnorm : Optional[tuple[float, float, float, float]]
        The radius of the new bodies. Default is None (determined by the
        mass with some default density assumption).
    radius_truncnorm : Optional[tuple[float, float, float, float]]
        The parameters for the truncated normal distribution of the
        radius of the new bodies. The tuple should be in the form
        (min, max, mu, sd). Default is None (auto-calculated), which
        means that the radius will be determined by the mass with
        the specified density.
    eccentricity_truncnorm : tuple[float, float, float, float]
        The parameters for the truncated normal distribution of the
        eccentricity of the orbit. Default is a degenerate distribution
        with mu = 0 and sd = 0 (circular orbit).
    G : float
        The gravitational constant. Default is `const.SIM_GRAVITY`.
    """
    if radius_truncnorm is not None and density_truncnorm is not None:
        raise ValueError("Either radius_truncnorm or density_truncnorm should be specified, but not both.")

    new_bodies = []
    for _ in range(num_bodies):
        min, max, mu, sd = dist_truncnorm
        a = (min - mu) / sd
        b = (max - mu) / sd
        dist = truncnorm.rvs(a, b, loc=mu, scale=sd, size=1)
        
        min, max, mu, sd = relative_mass_truncnorm
        a = (min - mu) / sd
        b = (max - mu) / sd
        rel_mass = truncnorm.rvs(a, b, loc=mu, scale=sd, size=1)
        mass = rel_mass * orbit_around.mass
        angle = random.uniform(0, 2 * math.pi)
        pos = vec2(orbit_around.pos.x + dist * math.cos(angle),
                   orbit_around.pos.y + dist * math.sin(angle))
        
        if radius_truncnorm is not None:
            min, max, mu, sd = radius_truncnorm
            a = (min - mu) / sd
            b = (max - mu) / sd
            radius = truncnorm.rvs(a, b, loc=mu, scale=sd, size=1)
        elif density_truncnorm is not None:
            min, max, mu, sd = density_truncnorm
            a = (min - mu) / sd
            b = (max - mu) / sd
            density = truncnorm.rvs(a, b, loc=mu, scale=sd, size=1)
            radius = (mass / density) ** (1 / 3)

        min, max, mu, sd = eccentricity_truncnorm
        a = (min - mu) / sd
        b = (max - mu) / sd
        eccentricity = truncnorm.rvs(a, b, loc=mu, scale=sd, size=1)

        initial_vel = get_orbital_body_velocity_around(
            orbit_around=orbit_around,
            pos=pos,            
            eccentricity=eccentricity,
            G=G)
    
        new_body = Body(pos, mass, orbit_around.color, radius)
        new_body.vel = initial_vel
        new_bodies.append(new_body)

    return new_bodies

def get_orbital_body_velocity_around(
        orbit_around : Body,
        initial_pos: vec2,
        eccentricity : float = 0, # default to circular orbit
        G: float = const.SIM_GRAVITY) -> vec2:
    """
    Get the initial velocity of a body in a circular or elliptical orbit around
    `orbit_around`. The initial position of the body is `initial_pos`.

    Parameters:
    -----------
    orbit_around : Body
        The body around which the new body will orbit.
    mass : float
        The mass of the new body.
    initial_pos : vec2
        The initial position of the new body.
    eccentricity : float
        The eccentricity of the orbit. Default is 0 (circular orbit).
    G : float
        The gravitational constant. Default is `const.SIM_GRAVITY`.
    radius : float
        The radius of the new body. Default is None (auto-calculated).

    Returns:
    --------
    vec2
        The initial velocity of the new body.
    """
    angle = math.atan2(initial_pos[1] - orbit_around.pos[1],
                       initial_pos[0] - orbit_around.pos[0])
    dist = (initial_pos - orbit_around.pos).length()
    eccentricity = max(0, min(eccentricity, 1))
    semi_major_axis = dist / (1 - eccentricity)
    speed = math.sqrt(G * orbit_around.mass * (2 / dist - 1 / semi_major_axis))
    vx = orbit_around.vel[0] - speed * math.cos(angle)
    vy = orbit_around.vel[1] + speed * math.sin(angle)
    return vec2(vx, vy)

def weighted_velocity(bodies: BodyList) -> vec2:
    """
    Calculate the weighted average velocity of a list of bodies, weighted by mass.
    """
    total_mass = sum(body.mass for body in bodies)
    weighted_vel = vec2(0, 0)

    for body in bodies:
        weighted_vel += body.vel * body.mass / total_mass

    return weighted_vel

def cross(o, a, b):
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)    


def polygon_area(polygon: list[vec2]) -> float:
    """
    Calculate the area of a polygon.
    """
    area = 0
    for i in range(len(polygon)):
        j = (i + 1) % len(polygon)
        area += polygon[i].x * polygon[j].y
        area -= polygon[i].y * polygon[j].x
    return abs(area) / 2

def random_colorizer_based_on_body_density(body: Body) -> tuple[int, int, int]:

    def project(value: float, old_min: float, old_max: float, new_min: float, new_max: float) -> float:
        return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
    
    r = project(math.log(body.mass), 0, 5, 0, 255) if body.mass <= 5 else 255
    g = project(math.log(body.density), 0, 1, 0, 255) if body.density <= 1 else 255
    b = project(math.log(body.kinetic_energy + 1), 0, 2, 0, 255) if body.kinetic_energy <= 2 else 255
    return (r, g, b)

def merge_bodies(body1: Body, body2: Body) -> Body:
    """
    Merge two bodies into a single body.

    The new body has the mass, position, and velocity of the center of mass
    of the two bodies, and the color is a weighted average of the two colors.

    Parameters:
    -----------
    body1 : Body
        The first body.
    body2 : Body
        The second body.

    Returns:
    --------
    The two bodies merged into a single body.
    """

    new_mass = body1.mass + body2.mass
    new_pos = (body1.pos * body1.mass + body2.pos * body2.mass) / new_mass
    new_color = tuple((a * body1.mass + b * body2.mass) / new_mass for a, b in zip(body1.color, body2.color))
    new_body = Body(pos=new_pos,
                    mass=new_mass,
                    base_color=new_color,
                    radius=None)
    new_body.density = (body1.density * body1.mass + body2.density * body2.mass) / new_mass
    new_body.vel = (body1.vel * body1.mass + body2.vel * body2.mass) / new_mass

    return new_body
