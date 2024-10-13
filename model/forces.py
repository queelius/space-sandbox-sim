from model.body import Body
from pygame.math import Vector2 as vec2
from utils.utils import *
import utils.const as const
from typing import Optional, Tuple
import math

def gravitational_force(body1: Body, body2: Body) -> vec2:
    """
    Calculate the gravitational force between two bodies.
    """
    delta_pos = body2.pos - body1.pos
    dist_sq = delta_pos.length_squared()
    dist = math.sqrt(dist_sq)
    force_mag = const.GRAVITY * body1.mass * body2.mass / dist_sq
    force = force_mag * (delta_pos / dist)  # Unit vector scaled by force magnitude
    return force

def merge_bodies(body1: Body, body2: Body) -> Optional[Body]:
    """
    Merge two bodies into a single body if they overlap sufficiently.
    """
    delta_pos = body2.pos - body1.pos
    dist = delta_pos.length()
    min_dist = body1.radius + body2.radius

    if dist > min_dist:
        return None

    overlap = overlap_area(body1.radius, body2.radius, dist)
    ratio = overlap / min(body1.area, body2.area)
    if ratio < const.MERGE_RATIO:
        return None

    new_mass = body1.mass + body2.mass
    new_pos = (body1.pos * body1.mass + body2.pos * body2.mass) / new_mass
    # new color is a weighted average of the two colors (using mass)
    new_color = tuple((a * body1.mass + b * body2.mass) / new_mass for a, b in zip(body1.color, body2.color))
    new_radius = (body1.radius**3 + body2.radius**3) ** (1 / 3)
    new_body = Body(new_pos, new_mass, new_color, new_radius)
    new_body.vel = (body1.vel * body1.mass + body2.vel * body2.mass) / new_mass
    return new_body

def collision_damping_force(body1: Body, body2: Body) -> vec2:
    """
    Calculate damping forces between two overlapping bodies.
    """
    displacement = body2.pos - body1.pos
    distance = displacement.length()
    penetration = (body1.radius + body2.radius) - distance

    if penetration < 0:
        return vec2(0, 0)

    collision_normal = displacement.normalize()
    relative_velocity = body1.vel - body2.vel
    velocity_along_normal = relative_velocity.x * collision_normal.x + relative_velocity.y * collision_normal.y
    F_damping = collision_normal * (-const.DAMPING * velocity_along_normal)
    return F_damping

def repulsion_force(body1: Body, body2: Body) -> vec2:
    """
    Calculate a repulsion force between two overlapping bodies.
    """

    delta_pos = body1.pos - body2.pos
    dist = delta_pos.length()
    min_dist = body1.radius + body2.radius

    if dist > min_dist:
        return vec2(0, 0)

    area = overlap_area(body1.radius, body2.radius, dist)
    force_mag = const.REPULSION_STRENGTH * area ** 1.5
    return force_mag * delta_pos.normalize()

def repulsion_forces(bh, body1: Body, body2: Body) -> vec2:
    """
    Compute repulsion forces for all overlapping body pairs.

    Parameters:
    -----------
    bodies : BodyList
        A list of body objects.
    """
    if bh.root is None:
        raise ValueError("Quadtree has not been built yet. Call build_tree() first.")

    overlapping_pairs = []
    bh.find_overlapping_pairs(bh.root, overlapping_pairs)

    # Compute repulsion forces for each overlapping pair
    for body1, body2 in overlapping_pairs:
        force = repulsion_force(body1, body2)
        body1.force += force
        body2.force -= force  # Newton's third law


    

    
    


