import math
from typing import Optional
from model.body import Body
from model.convex_hull import ConvexHull
from model.axis_aligned_bounding_box import AABB
from pygame.math import Vector2 as vec2

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

    def center_of_mass(self) -> vec2:
        """
        Calculate the center of mass of the composite. This is the mass-weighted
        average of the positions of the bodies in the composite.
        """
        return sum((body.pos * body.mass for body in self.bodies),
                   vec2(0, 0)) / self.total_mass()
    
    def centroid(self):
        """
        Calculate the centroid of the composite, the average position of the
        bodies in the composite.
        """
        return sum((body.pos for body in self.bodies),
                   vec2(0, 0)) / len(self.bodies)
    
    def total_mass(self) -> float:
        """
        Calculate the total mass of the composite.
        """
        return sum(body.mass for body in self.bodies)
    
    def hull_density(self) -> float:
        """
        Calculate the density of the composite.
        """
        return self.total_mass() / self.hull_area()
    
    def bounding_radius(self) -> float:
        """
        Calculate the bounding radius of the composite.
        """
        c = self.centroid()
        r = max((body.pos - c).length_squared() for body in self.bodies)
        return math.sqrt(r)
    
    def average_mass(self) -> float:
        """
        Calculate the average.
        """
        return self.total_mass() / len(self.bodies)    
   
    def bounding_box(self) -> AABB:
        """
        Calculate the bounding box of the composite.
        """
        return AABB(self.bodies)
    
    def hull_area(self) -> float:
        """
        Calculate the area of the convex hull of the composite.
        """
        return self.convex_hull().area

    def add_velocity(self, value: vec2) -> None:
        """
        Add velocity to the composite.
        """
        for body in self.bodies:
            body.vel += value
   
    def kinetic_energy(self) -> float:
        """
        Calculate the kinetic energy of the composite, which is
        the energy that is a function of its average velocity.
        """
        return 0.5 * self.total_mass() * self.center_of_mass_velocity().length_squared()
    
    def rotational_energy(self) -> float:
        """
        Calculate the rotational energy of the composite.
        """
        cv = self.center_of_mass_velocity()
        p = self.center_of_mass()
        E = 0
        for body in self.bodies:
            E += body.mass * (body.pos - p).cross(body.vel - cv)
        return 0.5 * E
    
    def center_of_mass_velocity(self) -> vec2:
        """
        Calculate the center of mass velocity of the composite.
        """
        return sum((body.vel * body.mass for body in self.bodies),
                   vec2(0,0)) / self.total_mass()
    
    def angular_momentum(self) -> float:
        """
        Calculate the angular momentum of the composite around its center of
        mass.
        """
        pivot = self.center_of_mass()
        return sum(body.mass * (body.pos - pivot).cross(body.vel) for body in self.bodies)
    
    def angular_velocity(self) -> float:
        """
        Calculate the angular velocity of the composite around its center of
        mass.
        """
        return self.angular_momentum() / self.moment_of_inertia()

    def moment_of_inertia(self) -> float:
        """
        Calculate the moment of inertia of the composite around its center of
        mass.
        """
        pivot = self.center_of_mass()
        return sum(body.mass * (body.pos - pivot).length_squared() for body in self.bodies)
    
    def linear_momentum(self) -> vec2:
        """
        Calculate the linear momentum of the composite.
        """
        return self.center_of_mass_velocity() * self.total_mass()

    def internal_energy(self) -> float:
        """
        Calculate the internal energy of the composite
        """
        cv = self.center_of_mass_velocity()
        E = 0
        for body in self.bodies:
            E += body.mass * (body.vel - cv).length_squared()
        return 0.5 * E
    
    def add_internal_energy(self, energy: float) -> None:
        """
        Add internal energy to the composite. We consider energy to be
        "internal" (even though each body has its own kinetic energy)
        to be energy that does not change the center of mass velocity
        or the rotational energy of the composite.
        
        To achieve this result, we do the following:

        1. Calculate the center of mass velocity.
        2. For each body, calculate the velocity relative to the center of mass.
        3. Add kinetic energy to each body in proportion to its mass.


        """
        cv = self.center_of_mass_velocity()
        for body in self.bodies:
            body.vel += (body.vel - cv).normalize() * math.sqrt(2 * energy / body.mass)


    def add_anglular_velocity(self, omega: float) -> None:
        """
        Add angular velocity to the composite.
        """
        cm = self.center_of_mass()
        for body in self.bodies:
            dp = body.pos - cm
            body.vel += vec2(-dp.y, dp.x).normalize() * omega

    def add_anglular_velocity2(self, omega: float) -> None:
        """
        Add angular velocity to the composite.
        """
        self.add_rotational_energy(0.5 * self.moment_of_inertia() * omega**2)

    def add_rotational_energy(self, energy: float) -> None:
        """
        Add rotational energy to the composite.
        """
        for body in self.bodies:
            dp = body.pos - self.center_of_mass()
            body.vel += vec2(-dp.y, dp.x).normalize() * math.sqrt(2 * energy / body.mass)

    def add_force(self, force: vec2) -> None:
        """
        Add a force to all bodies in the composite, scaled by the mass
        of each body so that the force causes the same acceleration
        in each body. Note that the total force on the composite is
        just `force`, so we don't just add `force` to each body.
        """
        total_mass = self.total_mass()
        for body in self.bodies:
            body.add_force(force * body.mass / total_mass)

    def add_torque(self, torque: float) -> None:
        """
        Add a torque to the composite. Note that torque is a property
        of the composite, not of any individual body, so we must distribute
        linear forces to each body to create the torque.
        """
        for body in self.bodies:
            dp = body.pos - self.center_of_mass()
            body.add_force(vec2(-dp.y, dp.x).normalize() * torque / dp.length())
            
    def convex_hull(self):
        """
        Calculate the convex hull of the composite.
        """
        return ConvexHull([body.pos for body in self.bodies])
    
    def average_color(self):
        """
        Calculate the average color of the composite.
        """

        # color is a Tuple[int, int, int]
        color = [0, 0, 0]
        for body in self.bodies:
            for i in range(3):
                color[i] += body.color[i] * body.mass

        total_mass = self.total_mass()
        for i in range(3):
            color[i] /= total_mass

        return tuple(color)
    
    def __iter__(self):
        return iter(self.bodies)
    
    def __len__(self):
        return len(self.bodies)
    
    def __getitem__(self, index):
        return self.bodies[index]
    
    def __setitem__(self, index, value):
        self.bodies[index] = value

    def __str__(self):
        return f"CompositeBody(center_of_mass={self.center_of_mass()}, mass={self.total_mass():.3}, area={self.area():.3})"
    
    def __repr__(self):
        return f"CompositeBody({self.bodies})"
    
    def __add__(self, other):
        """
        Add two composite bodies together.
        """
        return CompositeBody(self.bodies + other.bodies)

    def __sub__(self, other):
        """
        Subtract two composite bodies.
        """
        return CompositeBody([body for body in self.bodies if body not in other.bodies])
    
    def __eq__(self, other):
        """
        Check if two composite bodies are equal.
        """
        return set(self.bodies) == set(other.bodies)
    
    def __contains__(self, body):
        """
        Check if a body is in the composite.
        """
        return body in self.bodies
    
    def __hash__(self):
        return hash(tuple(self.bodies))
    
    def __bool__(self):
        return self.bodies != []

    def statistics(self):
        stats = {
            "mass": self.total_mass(),
            "center_of_mass": {
                "position": self.center_of_mass(),
                "velocity": self.center_of_mass_velocity(),
            },
            "mass_properties": {
                "average_mass": self.average_mass(),
                "linear_momentum": self.linear_momentum(),
                "moment_of_inertia": self.moment_of_inertia(),
                "bounding_radius": self.bounding_radius(),
            },
            "energy": {
                "kinetic_energy": self.kinetic_energy(),
                "internal_energy": self.internal_energy(),
                "rotational_energy": self.rotational_energy(),
                "total_energy": self.kinetic_energy() + self.internal_energy() + self.rotational_energy(),  # Sum of energies
            },
            "angular_motion": {
                "angular_velocity_radians": self.angular_velocity(),
                "angular_velocity_degrees": math.degrees(self.angular_velocity()),
                "angular_momentum": self.angular_momentum(),
                "rotation_period": 2 * math.pi / self.angular_velocity() if self.angular_velocity() != 0 else None,  # Period in seconds for one full rotation
            },
            "hull_properties": {
                "hull_area": self.hull_area(),
                "hull_density": self.hull_density(),
            },
            # Additional statistics
            "velocity_magnitude": math.sqrt(sum(v**2 for v in self.center_of_mass_velocity())),  # Speed of the composite
            "total_momentum": math.sqrt(sum(m**2 for m in self.linear_momentum())),  # Total magnitude of linear momentum
            "momentum_to_energy_ratio": (math.sqrt(sum(m**2 for m in self.linear_momentum())) / 
                                        self.kinetic_energy()) if self.kinetic_energy() != 0 else None,  # New stat for ratio of momentum to energy
            "num_bodies": len(self.bodies),
            "temperature": self.temperature() if hasattr(self, 'temperature') else None,  # Hypothetical, if you model temperature
        }
        return stats
