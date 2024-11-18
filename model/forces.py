from model.body import Body
from pygame.math import Vector2 as vec2
from utils.circle_tools import CircleTools
import utils.const as const
from typing import Callable
from events.event_bus import EventBus
from model.sim_state import SimState

def generate_collision_damping_force(
        event_bus: EventBus,
        damping: float = const.REPULSION_DAMPING) -> Callable[[Body, Body], vec2]:
    """
    Generate a functino that calculates a collision damping force between two
    bodies.

    Parameters:
    -----------
    damping : float
        The damping coefficient.

    Returns:
    --------
    Callable[[Body, Body], vec2]
        A function that calculates the collision damping force between two bodies.
        This causes the two bodies to lose energy when they collide.

        Parameters:
        -----------
        body1 : Body
            The first body.
        body2 : Body
            The second body.

        Returns:
        --------
        vec2
            The collision damping force between the two bodies.
    """
    def collision_damping_force(body1: Body, body2: Body) -> vec2:
        displacement = body2.pos - body1.pos
        distance = displacement.length()
        penetration = (body1.radius + body2.radius) - distance

        if penetration < 0:
            return vec2(0, 0)

        collision_normal = displacement.normalize()
        rel_vel = body1.vel - body2.vel
        vel_along_normal = (rel_vel.x * collision_normal.x +
                            rel_vel.y * collision_normal.y)
        F_damp = collision_normal * (-damping * vel_along_normal)

        # work = F_damp * d
        # d is the distance over which the F_damp is applied
        # solution steps:
        # 1) d = v * t
        # 2) v = a * t
        # 3) a = F_damp / m
        # -> d = (F_damp / m) * t^2
        d = (F_damp.length() / body1.mass) * SimState().time_step ** 2
        W = F_damp.length() * d

        #event_bus.publish("collision_damping", {
        #    "body1": body1,
        #    "body2": body2,
        #    "penetration": penetration,
        #    "damping_force": F_damp,
        #    "energy_loss": W
        #})
        return F_damp
    
    return collision_damping_force

def generate_repulsion_force(
        event_bus: EventBus,
        strength: float = const.REPULSION_STRENGTH,
        factor: Callable[[float, float, float], float] = CircleTools.intersection_area,
        slack: float = 1e-3,
        beta: float = 1.5) -> Callable[[Body, Body], vec2]:
    """
    Generate a function that calculates a repulsion force between two bodies.

    Parameters:
    -----------
    strength : float
        The strength of the repulsion force.
    factor : Callable[[float, float, float], float]
        A function that calculates the factor for the repulsion force. The
        first two arguments are the radii of the two bodies, and the third
        argument is the distance between the two bodies.

        Default is `CircleTools.intersection_area`. Other reasonable choices
        are `CircleTools.chord_length` and `CircleTools.penetration_depth`.
    
    beta : float
        The power to which the factor is raised.

    Returns:
    --------
    Callable[[Body, Body], vec2]
        A function that calculates the repulsion force between two bodies
        with a given strength.

        Parameters:
        -----------
        body1 : Body
            The first body.
        body2 : Body
            The second body.
        
        Returns:
        --------
        vec2
            The repulsion force between the two bodies.
        
    """
    
    def repulsion_force(body1: Body, body2: Body) -> vec2:
        delta_pos = body1.pos - body2.pos
        dist = delta_pos.length()
        min_dist = body1.radius + body2.radius + slack

        if dist > min_dist:
            return vec2(0, 0)

        g = factor(body1.radius, body2.radius, dist)
        f = strength * g ** beta

        # event_bus.publish("repulsion", {
        #     "body1": body1,
        #     "body2": body2,
        #     "distance": dist,
        #     "repulsion_force": f
        # })

        return f * delta_pos.normalize()
    
    return repulsion_force


def generate_leonard_jones_like_force(
        event_bus: EventBus,
        cutoff_distance: float = 10.0,
        equilibrium_distance: float = 1.0,
        epsilon: float = 4.0,
        alpha: float = 6.0) -> Callable[[Body, Body], vec2]:
    """
    Generate a function that calculates a Leonard-Jones-like force between two bodies.

    Parameters:
    -----------
    cutoff_distance : float
        The distance at which the force is cut off.
    equilibrium_distance : float
        The distance at which the force is at equilibrium.
    alpha : float
        The alpha parameter in the Leonard-Jones force.

    Returns:
    --------
    Callable[[Body, Body], vec2]
        A function that calculates the Leonard-Jones-like force between two bodies.

        Parameters:
        -----------
        body1 : Body
            The first body.
        body2 : Body
            The second body.

        Returns:
        --------
        vec2
            The Leonard-Jones-like force between the two bodies
    """    
    def lj_like_force(body1: Body, body2: Body) -> vec2:
        delta_pos = body1.pos - body2.pos
        dist = delta_pos.length()
        min_dist = body1.radius + body2.radius + cutoff_distance

        if dist > min_dist:
            return vec2(0, 0)
        
        r_e = body1.radius + body2.radius + equilibrium_distance
        f_mag = (alpha * epsilon / dist * ( (r_e / dist) ** (2*alpha) -
                                            (r_e / dist) ** alpha))
        f = f_mag * delta_pos.normalize()
        
        event_bus.publish("lj_like_force", {
            "body1": body1,
            "body2": body2,
            "distance": dist,
            "force": f
        })
        return f
    
    return lj_like_force


def generate_gravitational_force(
        event_bus: EventBus,
        G: float = const.SIM_GRAVITY) -> Callable[[Body, Body], vec2]:
    """
    Calculate the gravitational force between two bodies.

    Parameters:
    -----------
    G : float
        The gravitational constant.

    Returns:
    --------
    Callable[[Body, Body], vec2]
        A function that calculates the gravitational force between two bodies.

        Parameters:
        -----------
        body1 : Body
            The first body.
        body2 : Body
            The second body.

        Returns:
        --------
        vec2
            The gravitational force between the two bodies
    """
    def gravitational_force(body1: Body, body2: Body) -> vec2:
        delta_pos = body2.pos - body1.pos
        dist_sq = delta_pos.length_squared()
        #dist = math.sqrt(dist_sq)
        force_mag = G * body1.mass * body2.mass / dist_sq
        force = force_mag * delta_pos.normalize()
        return force
    
    return gravitational_force



