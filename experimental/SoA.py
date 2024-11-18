#import cupy as cp
import numpy as np

class SimBodySoA:
    """

    """
    def __init__(self, dt, max_bodies, max_springs, integrator):
        self.dt = dt
        self.positions_x = np.zeros(max_bodies, dtype=np.float32)
        self.positions_y = np.zeros(max_bodies, dtype=np.float32)
        self.old_positions_x = np.zeros(max_bodies, dtype=np.float32)
        self.old_positions_y = np.zeros(max_bodies, dtype=np.float32)
        self.forces_x = np.zeros(max_bodies, dtype=np.float32)
        self.forces_y = np.zeros(max_bodies, dtype=np.float32)
        self.masses = np.ones(max_bodies, dtype=np.float32)

        # an array of spring tuples
        self.springs_equilibrium = np.zeros(max_springs, dtype=np.float32)
        self.springs_positions_x = np.zeros(max_springs, dtype=np.float32)
        self.springs_positions_y = np.zeros(max_springs, dtype=np.float32)
        self.springs_stiffness = np.zeros(max_springs, dtype=np.float32)
        self.springs_damping = np.zeros(max_springs, dtype=np.float32)
        self.springs_break_force = np.zeros(max_springs, dtype=np.float32)
        self.springs_break_distance_factor = np.zeros(max_springs, dtype=np.float32)

    def update(self):
        grav_accs = (self.forces_x / self.masses[:, np.newaxis], self.forces_y / self.masses[:, np.newaxis])

        
        


        self.integrator(self.positions, self.old_positions, grav_accs)

    def add_bodies(self, positions, masses):
        # cycle positions or masses if they are not the same length
        if len(positions) != len(masses):
            if len(positions) > len(masses):
                masses = np.hstack([masses, np.ones(len(positions) - len(masses), dtype=np.float32)])
            else:
                positions = np.vstack([positions, np.zeros((len(masses) - len(positions), 2), dtype=np.float32)])            
                
        self.positions = np.vstack([self.positions, positions])
        self.old_positions = np.vstack([self.old_positions, positions])
        self.forces = np.vstack([self.forces, np.zeros((len(positions), 2), dtype=np.float32)])
        self.masses = np.hstack([self.masses, masses])

    def get_bodies(self, indices):
        return [Body(self, index) for index in indices]
    
    def apply_force(self, indices, force):
        self.forces[indices] += force


class Body:
    """
    A body in the simulation. This is a simple object that wraps the data
    in the SoA representation and provides a more object-oriented interface
    to the data. For the most part, we avoid use of `Body` objects
    explicitly in the simulation code, but they are useful for the
    user interface and for testing.
    """
    def __init__(self, data: BodyListSoA, index):
        self.data = data
        self.index = index

    @property
    def pos(self):
        return self.data.positions[self.index]

    @pos.setter
    def pos(self, value):
        self.data.positions[self.index] = value

    @property
    def vel(self):
        return (self.data.positions[self.index] - self.data.old_positions[self.index]) / self.data.dt

    @vel.setter
    def vel(self, value):
        self.data.old_positions[self.index] = self.data.positions[self.index] - value * self.data.dt

    def apply_force(self, force):
        self.data.forces[self.index] += force
