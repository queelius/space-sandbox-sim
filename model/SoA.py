import cupy as cp

class SoA:
    def __init__(self, dt, num_bodies, integrator):
        self.dt = dt
        self.positions = cp.zeros((num_bodies, 2), dtype=cp.float32)
        self.old_positions = cp.zeros((num_bodies, 2), dtype=cp.float32)
        self.forces = cp.zeros((num_bodies, 2), dtype=cp.float32)
        self.masses = cp.ones(num_bodies, dtype=cp.float32)  # Example mass initialization

    def update(self):
        accs = self.forces / self.masses[:, cp.newaxis]
        self.integrator(self.positions, self.old_positions, accs)

    def add_bodies(self, positions, masses):
        # cycle positions or masses if they are not the same length
        if len(positions) != len(masses):
            if len(positions) > len(masses):
                masses = cp.hstack([masses, cp.ones(len(positions) - len(masses), dtype=cp.float32)])
            else:
                positions = cp.vstack([positions, cp.zeros((len(masses) - len(positions), 2), dtype=cp.float32)])            
                
        self.positions = cp.vstack([self.positions, positions])
        self.old_positions = cp.vstack([self.old_positions, positions])
        self.forces = cp.vstack([self.forces, cp.zeros((len(positions), 2), dtype=cp.float32)])
        self.masses = cp.hstack([self.masses, masses])

    def get_bodies(self, indices):
        return [Body(self, index) for index in indices]
    
    def apply_force(self, indices, force):
        self.forces[indices] += force


class Body:
    def __init__(self, SoA, index):
        self.SoA = SoA
        self.index = index

    @property
    def pos(self):
        return self.SoA.positions[self.index]

    @pos.setter
    def pos(self, value):
        self.SoA.positions[self.index] = value

    @property
    def vel(self):
        return (self.SoA.positions[self.index] - self.SoA.old_positions[self.index]) / self.SoA.dt

    @vel.setter
    def vel(self, value):
        self.SoA.old_positions[self.index] = self.SoA.positions[self.index] - value * self.SoA.dt

    def apply_force(self, force):
        self.SoA.forces[self.index] += force
