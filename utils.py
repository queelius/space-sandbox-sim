import math
from pygame.math import Vector2 as vec2
import random
import const
from body import Body
from body_list import BodyList

def overlap_circle(r1, r2, d) -> bool:
    """
    Check if two circles with radii r1 and r2 overlap when separated by distance d.
    """
    return d < r1 + r2

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


def overlap_chord(r1, r2, d) -> float:
    """
    Calculate the length of the chord formed by the intersection of two circles
    with radii r1 and r2 and centers separated by distance d.
    """
    # If they do not overlap, return 0
    if d >= r1 + r2:
        return 0

    # If one circle is inside the other, return 0
    if d <= abs(r1 - r2):
        return 0

    # Calculate the length of the chord formed by the intersection
    part = (d**2 + r1**2 - r2**2) / (2 * d)
    return 2 * math.sqrt(r1**2 - part**2)

def overlap_proj(r1, r2, d) -> float:
    """
    Calculate the projected overlap of two circles along the line connecting
    their centers.
    """
    return max(0, r1 + r2 - d)

def overlap_area(r1, r2, d) -> float:
    """
    Calculate the area of overlap between two circles with radii r1 and r2
    separated by a distance d.
    """
    # If the circles do not overlap, return 0
    if d >= r1 + r2:
        return 0

    # If one circle is completely inside the other, return the area of the smaller circle
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2

    # Calculate the area of the overlapping region
    part1 = r1**2 * math.acos((d**2 + r1**2 - r2**2) / (2 * d * r1))
    part2 = r2**2 * math.acos((d**2 + r2**2 - r1**2) / (2 * d * r2))
    part3 = 0.5 * math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))

    return part1 + part2 - part3

def add_orbital_bodies(
        num_bodies : int,
        bodies : BodyList,
        other_body : Body,
        dist_mu: float,
        dist_var: float,
        rel_mass_mu: float,
        rel_mass_var: float,
        eccentricity : float = 0) -> None:
    """
    Add a number of bodies in orbit around an `other_body`, ideally that is
    relatively large so that the system is relatively stable.
    """
    for _ in range(num_bodies):
        dist = random.gauss(dist_mu, dist_var)
        rel_mass = random.gauss(rel_mass_mu, rel_mass_var)
        mass = rel_mass * other_body.mass
        angle = random.uniform(0, 2 * math.pi)
        pos = vec2(other_body.pos[0] + dist * math.cos(angle),
                   other_body.pos[1] + dist * math.sin(angle))
        add_orbital_body(bodies=bodies,
                         other_body=other_body,
                         pos=pos,
                         mass=mass,
                         eccentricity=eccentricity)

def add_orbital_body(
        bodies : BodyList,
        other_body : Body,
        pos : vec2,
        mass: float,
        eccentricity : float = 0, # default to circular orbit
        radius=None) -> Body:
    """
    Add a body in (possibly eccentric) orbit around `other_body`.
    """
    angle = math.atan2(pos[1] - other_body.pos[1], pos[0] - other_body.pos[0])
    dist = (pos - other_body.pos).length()
    if eccentricity >= 1:
        eccentricity = 1-1e-6
    semi_major_axis = dist / (1 - eccentricity)
    speed = math.sqrt(const.GRAVITY * other_body.mass * (2 / dist - 1 / semi_major_axis))
    vx = other_body.velocity[0] - speed * math.sin(angle)
    vy = other_body.velocity[1] + speed * math.cos(angle)
    body = Body(pos=pos, mass=mass, base_color=random.choice(const.COLORS), radius=radius)
    body.velocity = vec2(vx, vy)
    bodies.add(body)
    return body

def weighted_velocity(bodies: BodyList) -> vec2:
    """
    Calculate the weighted average velocity of a list of bodies, weighted by mass.
    """
    total_mass = sum(body.mass for body in bodies)
    weighted_vel = vec2(0, 0)

    for body in bodies:
        weighted_vel += body.velocity * body.mass / total_mass

    return weighted_vel


def convex_hull(bodies: list[Body]) -> list[vec2]:
    """
    Calculate the convex hull of a cluster of bodies.
    """
    points = [body.pos for body in bodies]
    hull = []
    if len(points) < 3:
        return points

    # Find the leftmost point
    l = min(points, key=lambda p: p[0])

    # Sort the points based on the angle they make with the leftmost point
    points.sort(key=lambda p: math.atan2(p[1] - l[1], p[0] - l[0]))

    hull = [points[0], points[1]]
    for i in range(2, len(points)):
        while len(hull) > 1 and (points[i] - hull[-1]).cross(hull[-1] - hull[-2]) <= 0:
            hull.pop()
        hull.append(points[i])

    return hull