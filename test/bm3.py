import numpy as np
import time

# Gravitational constant
G = 6.67430e-11

# Number of frames per second
TARGET_FPS = 60

class CPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt

        # Initialize random positions, velocities, and masses
        self.positions = np.random.rand(num_bodies, 3) * 1000.0  # Random positions in a 1000x1000x1000 box
        self.velocities = np.zeros((num_bodies, 3))  # Initially at rest
        self.masses = np.random.rand(num_bodies) * 1e24  # Random masses between 0 and 1e24 kg

    def compute_forces(self):
        # Calculate pairwise differences for all positions
        delta_pos = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]  # Shape (N, N, 3)

        # Calculate pairwise distances (with small epsilon to avoid division by zero)
        dist_sq = np.sum(delta_pos ** 2, axis=2) + 1e-10  # Shape (N, N)
        dist = np.sqrt(dist_sq)

        # Avoid self-interaction by setting inverse distances for self-pairs to zero
        inv_dist_cube = np.where(dist > 1e-10, 1.0 / (dist_sq * dist), 0.0)  # Shape (N, N)

        # Gravitational force calculation: F = G * (m_i * m_j / r^2) * (r_ij / |r_ij|)
        forces = G * (self.masses[:, np.newaxis] * self.masses[np.newaxis, :]).reshape(self.num_bodies, self.num_bodies, 1) * inv_dist_cube[:, :, np.newaxis] * delta_pos

        # Sum the forces for each body (axis=1 sums over other bodies)
        total_forces = np.sum(forces, axis=1)

        # Local interaction: apply additional forces if the distance is below the cutoff
        close_bodies = dist < self.cutoff_distance
        repulsive_forces = np.where(close_bodies[:, :, np.newaxis], -0.1 * delta_pos, 0.0)
        total_forces += np.sum(repulsive_forces, axis=1)

        return total_forces

    def update(self):
        # Compute forces on all bodies
        forces = self.compute_forces()

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
bodies_list = [1000, 5000, 10000, 20000]
cutoff_distance = 50.0  # Example cutoff distance for local interactions

for num_bodies in bodies_list:
    fps = benchmark_simulation(num_bodies, cutoff_distance)
    if fps < TARGET_FPS:
        print(f"Cannot simulate {num_bodies} bodies at 60 FPS. Stopping.")
        break
