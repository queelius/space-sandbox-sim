import utils.const as const
from pygame.math import Vector2 as vec2
import math
from typing import Tuple
from model.sim_state import SimState

class Body:
    def __init__(self, pos: vec2,
                 mass: float,
                 base_color: Tuple[int, int, int],
                 radius=None):
        """
        Initialize Body with a position vector and mass.
        """
        self._pos : vec2 = vec2(pos)  # Position vector
        self._old_pos : vec2 = vec2(pos)  # Previous position vector
        self.mass : float = mass
        self.radius : float = self.mass ** (1 / 3) if radius is None else radius
        self.force : vec2 = vec2(0, 0)
        self.base_color = base_color

    @property
    def pos(self) -> vec2:
        """
        Get the position of the body.
        """
        return self._pos
    
    @pos.setter
    def pos(self, value: vec2) -> None:
        """
        Set the position of the body.
        """
        delta = self._pos - self._old_pos
        self._pos = value
        self._old_pos = value - delta

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
    def escape_velocity(self) -> float:
        """
        Calculate the escape velocity of the body.
        """
        return math.sqrt(2 * const.SIM_GRAVITY * self.mass / self.radius)

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
        self.mass = value * self.area

    @property
    def color(self) -> Tuple[int, int, int]:
        """
        Get the color of the body.

        TODO: We might modulate the `base_color` based on the density of the
              body or something else.
        """
        return self.base_color
    
    @property
    def vel(self) -> vec2:
        """
        Calculate the velocity vector from position and old position.
        """
        return (self._pos - self._old_pos) / SimState().time_step

    @vel.setter
    def vel(self, value: vec2) -> None:
        """
        Set the velocity vector by adjusting the old position.
        """
        self._old_pos = self._pos - value * SimState().time_step
    
    def reset_force(self) -> None:
        self.force = vec2(0, 0)

    def __str__(self) -> str:
        return f"Body(pos={self.pos}, vel={self.vel}, mass={self.mass:.3}, radius={self.radius:.3})"
    
    def __repr__(self) -> str:
        return f"Body({self.pos}, {self.mass}, {self.color}, {self.radius})"
    
    def add_force(self, force: vec2) -> None:
        """
        Accumulate forces.

        Parameters:
        -----------
        force : vec2
            The force to accumulate.
        """
        self.force += force

    def update(self) -> None:
        """
        This implements the Verlet integration method:

            x(t + dt) = 2 * x(t) - x(t - dt) + a * dt^2

        Verlet integration is a numerical method used to integrate Newton's
        equations of motion. It is a symplectic integrator, meaning that it
        conserves energy (up to numerical errors). It is of second order O(dt^2),
        which means that the error in the position is proportional to the square
        of the time step, and the error in the velocity is proportional to the
        time step.
        """
        tmp_pos = self._pos.copy()
        a = self.force / self.mass
        dt = SimState().time_step

        self._pos += self._pos - self._old_pos + a * dt ** 2
        self._old_pos = tmp_pos

    @property
    def kinetic_energy(self) -> float:
        """
        Calculate the kinetic energy of the body.
        """
        return 0.5 * self.mass * self.vel.length_squared()
    
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
        v = self.vel.normalize() * math.sqrt(2 * abs(energy) / self.mass)
        self.vel += v if energy > 0 else -v

        
