import const
import pygame
from pygame.math import Vector2 as vec2
import math
from typing import Tuple

class Body:
    def __init__(self, pos: vec2,
                 mass: float,
                 base_color: Tuple[int, int, int],
                 radius=None):
        """
        Initialize Body with a position vector and mass.
        """
        self.pos : vec2 = vec2(pos)  # Position vector
        self.old_pos : vec2 = vec2(pos)  # Previous position vector
        self.mass : float = mass
        self.radius : float = self.mass ** (1 / 3) if radius is None else radius
        self.force : vec2 = vec2(0, 0)
        self.base_color = base_color

    @property
    def area(self) -> float:
        """
        Calculate the area of the body.
        """
        return math.pi * self.radius ** 2
    
    @area.setter
    def area(self, value: float) -> None:
        """
        Adjust the radius based on the new area value.
        """
        self.radius = math.sqrt(value / math.pi)

    @property
    def event_horizon(self) -> float:
        """
        Calculate the event horizon of the body.
        """
        return 2 * const.GRAVITY * self.mass / const.LIGHT_SPEED**2
    
    @property
    def relativistic_mass(self) -> float:
        """
        Calculate the relativistic mass of the body
        """
        return self.mass / math.sqrt(1 - self.velocity.length_squared() / const.LIGHT_SPEED**2)
    
    @property
    def escape_velocity(self) -> float:
        """
        Calculate the escape velocity of the body.
        """
        return math.sqrt(2 * const.GRAVITY * self.mass / self.radius)

    @property
    def density(self) -> float:
        """
        Calculate the density of the celestial object.
        """
        return self.mass / self.area
    
    @density.setter
    def density(self, value: float) -> None:
        """
        Adjust the mass based on the new density value.
        """
        self.mass = value * self.area()

    @property
    def color(self) -> Tuple[int, int, int]:
        """
        Get the color of the body.
        
        TODO: let color be a function of `base_color` and other properties.
        """
        return self.base_color
    
    @property
    def velocity(self) -> vec2:
        """
        Calculate the velocity vector from position and old position.
        """
        return (self.pos - self.old_pos) / const.DT

    @velocity.setter
    def velocity(self, value: vec2) -> None:
        """
        Set the velocity vector by adjusting the old position.
        """
        self.old_pos = self.pos - value * const.DT
    
    def reset_force(self) -> None:
        self.force = vec2(0, 0)

    def __str__(self) -> str:
        return f"Body(x={self.pos.x:.3}, y={self.pos.y:.3}, mass={self.mass:.3}, radius={self.radius:.3})"
    
    def __repr__(self) -> str:
        return f"Body({self.pos.x}, {self.mass}, {self.color}, {self.radius})"
    
    def add_force(self, force: vec2) -> None:
        """
        Accumulate forces.

        Args:
            force (vec2): The force vector to add.
        """
        self.force += force

    def update(self) -> None:
        """
        Update the position based on current forces (Verlet integration, which
        is O(DT^2) accurate).
        """
        tmp_pos = self.pos.copy()
        self.pos += self.pos - self.old_pos + self.force / self.mass * const.DT**2
        self.old_pos = tmp_pos

    @property
    def kinetic_energy(self) -> float:
        """
        Calculate the kinetic energy of the body.
        """
        return 0.5 * self.mass * self.velocity.length_squared()
    
    @property
    def rotational_energy(self) -> float:
        """
        Calculate the rotational energy of the body. Since this body is
        an "atomic" body, it has no rotational energy.
        """
        return 0.0
    
    def add_kinetic_energy(self, energy: float) -> None:
        """
        Add kinetic energy to the body. Since energy can be positive or negative,
        the velocity can be increased or decreased.
        """
        v = self.velocity.normalize() * math.sqrt(2 * abs(energy) / self.mass)
        self.velocity += v if energy > 0 else -v

        
