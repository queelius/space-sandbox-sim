import math
from model.body import Body
from pygame.math import Vector2 as vec2
import utils.utils as utils


class CompositeBody:
    """
    A class to represent a set of bodies as a single composte body,
    although we do not typically apply forces to the composite body
    in the simulation -- but we can intervene and in the future we
    may have special forces that act on composite bodies as a whole.

    Note that this is a transient simulation object. Each time step, we
    reconstruct composite bodies from spring networks, so we do not need
    to worry about the state of the composite body between time steps.
    """
    def __init__(self, bodies: list[Body]):
        self.bodies = bodies

    @property
    def pos(self) -> Body:
        """
        Calculate the center of mass of the cluster.
        """
        total_mass = self.mass        
        # compute the center of mass
        com = vec2(0, 0)
        for body in self.bodies:
            com += body.pos * body.mass
        com /= total_mass
        return com
    
    @property
    def mass(self) -> float:
        """
        Calculate the total mass of the cluster.
        """
        return sum(body.mass for body in self.bodies)

    @property    
    def vel(self) -> vec2:
        """
        Calculate the average velocity of the cluster.
        """
        return sum(body.vel * body.mass for body in self.bodies) / self.mass
    
    @property
    def kinetic_energy(self) -> float:
        """
        Calculate the kinetic energy of the cluster, which is
        the energy that is a function of its average velocity.
        """
        return 0.5 * self.mass * self.velocity.length_squared()
    
    @property
    def thermal_energy(self) -> float:
        """
        Calculate the thermal energy of the cluster, which is the
        the kinetic energy of the cluster relative to the center of 
        velocity of the cluster.
        """
        cv = self.velocity
        E = 0
        for body in self.bodies:
            E += body.mass * (body.vel - cv).length_squared()
        return 0.5 * E
    
    @property
    def radius(self) -> float:
        """
        Calculate the bounding radius of the cluster.
        """
        r = 0
        for body in self.bodies:
            r = max(r, (body.pos - self.pos).length())
        return r
    
    @property
    def rotational_energy(self) -> float:
        """
        Calculate the rotational energy of the cluster.
        """
        cv = self.velocity
        E = 0
        for body in self.bodies:
            E += body.mass * (body.pos - self.pos).cross(body.vel - cv)
        return 0.5 * E
    
    def add_thermal_energy(self, energy: float) -> None:
        """
        Add thermal energy to the cluster.
        """
        cv = self.velocity
        for body in self.bodies:
            body.vel += (body.vel - cv).normalize() * math.sqrt(2 * energy / body.mass)

    def add_rotational_energy(self, energy: float) -> None:
        """
        Add rotational energy to the cluster.
        """
        cv = self.velocity
        for body in self.bodies:
            body.vel += (body.pos - self.pos).cross(cv) * math.sqrt(2 * energy / body.mass)

    def add_force(self, force: vec2) -> None:
        """
        Add a force to all bodies in the cluster, scaled by the mass
        of each body so that the force causes the same acceleration
        in each body. Note that the total force on the cluster is
        just `force`, so we don't just add `force` to each body.
        """
        for body in self.bodies:
            body.add_force(force * body.mass / self.mass)

    def add_torque(self, torque: float) -> None:
        """
        Add a torque to the cluster. Note that torque is a property
        of the cluster, not of any individual body, so we must distribute
        linear forces to each body to create the torque.
        """
        for body in self.bodies:
            r = body.pos - self.pos
            tau = r.cross(torque) * body.mass / self.mass
            print(tau)
            body.add_force(1)
            
    def convex_hull(self):
        """
        Calculate the convex hull of the cluster.
        """
        return utils.convex_hull(self.bodies)
    
    def __iter__(self):
        return iter(self.bodies)
    
    def __len__(self):
        return len(self.bodies)
    

