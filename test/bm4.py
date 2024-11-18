import numpy as np
import time
from numba import jit, prange

# Gravitational constant
G = 6.67430e-11

# Number of frames per second
TARGET_FPS = 60

# Standalone function for computing forces
@jit(nopython=True, parallel=True)
def compute_forces(positions, masses, num_bodies, cutoff_distance):
    total_forces = np.zeros((num_bodies, 3))  # Initialize forces for each body to zero

    for i in prange(num_bodies):
        force_i = np.zeros(3)  # Force acting on body `i`
        
        for j in range(num_bodies):
            if i == j:
                continue  # Skip self-interaction

            # Calculate the difference in positions
            delta_pos = positions[j] - positions[i]

            # Calculate the squared distance
            dist_sq = np.sum(delta_pos ** 2) + 1e-10  # Add epsilon to avoid division by zero
            dist = np.sqrt(dist_sq)

            # Calculate inverse of distance cube
            inv_dist_cube = 1.0 / (dist_sq * dist)

            # Gravitational force calculation: F = G * (m_i * m_j / r^2) * (r_ij / |r_ij|)
            force = G * masses[i] * masses[j] * inv_dist_cube * delta_pos

            # Add the force from body `j` to the total force on body `i`
            force_i += force

            # Check for local interaction (e.g., repulsion)
            if dist < cutoff_distance:
                repulsive_force = -0.1 * delta_pos
                force_i += repulsive_force
        
        # Store the total force on body `i`
        total_forces[i] = force_i

    return total_forces


class CPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt

        # Initialize random positions, velocities, and masses
        self.positions = np.random.rand(num_bodies, 3) * 1000.0  # Random positions in a 1000x1000x1000 box
        self.velocities = np.zeros((num_bodies, 3))  # Initially at rest
        self.masses = np.random.rand(num_bodies) * 1e24  # Random masses between 0 and 1e24 kg

    def update(self):
        # Compute forces on all bodies using the standalone function
        forces = compute_forces(self.positions, self.masses, self.num_bodies, self.cutoff_distance)

        # Update velocities and positions
        self.velocities += forces / self.masses[:, np.newaxis] * self.dt
        self.positions += self.velocities * self.dt

    def simulate(self, num_steps):
        start_time = time.time()

        for step in range(num_steps):
            self.update()

        end_time = time.time()
        return end_time - start_time


# Benchmark the simulation to see how many bodies can be simulated at 60 FPS
def benchmark_simulation(num_bodies, cutoff_distance, duration=10):
    sim = CPUNBodySimulation(num_bodies, cutoff_distance)

    # Assume we need to run for 60 FPS for `duration` seconds
    num_steps = int(TARGET_FPS * duration)

    elapsed_time = sim.simulate(num_steps)
    avg_fps = num_steps / elapsed_time

    print(f"Simulated {num_bodies} bodies for {duration} seconds.")
    print(f"Average FPS: {avg_fps:.2f}")

    return avg_fps


# Try different numbers of bodies to see how many we can simulate at 60 FPS
bodies_list = [2000, 5000, 10000, 20000]
cutoff_distance = 50.0  # Example cutoff distance for local interactions

for num_bodies in bodies_list:
    fps = benchmark_simulation(num_bodies, cutoff_distance)
    if fps < TARGET_FPS:
        print(f"Cannot simulate {num_bodies} bodies at 60 FPS. Stopping.")
        break
