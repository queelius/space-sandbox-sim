import cupy as cp
import time

# Gravitational constant
G = 6.67430e-11

# Custom CUDA kernel for force calculation
force_kernel = cp.RawKernel(r'''
extern "C" __global__
void compute_forces(double* positions, double* velocities, double* masses, double* forces, int num_bodies, double cutoff_distance, double G) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= num_bodies) return;
    
    double force[3] = {0.0, 0.0, 0.0};
    for (int j = 0; j < num_bodies; j++) {
        if (i == j) continue;

        double delta_pos[3];
        for (int k = 0; k < 3; k++) {
            delta_pos[k] = positions[j * 3 + k] - positions[i * 3 + k];
        }

        double dist_sq = delta_pos[0] * delta_pos[0] + delta_pos[1] * delta_pos[1] + delta_pos[2] * delta_pos[2] + 1e-10;
        double dist = sqrt(dist_sq);
        double inv_dist_cube = 1.0 / (dist_sq * dist);

        // Gravitational force
        double force_scalar = G * masses[i] * masses[j] * inv_dist_cube;
        for (int k = 0; k < 3; k++) {
            force[k] += force_scalar * delta_pos[k];
        }

        // Apply repulsive force if within cutoff distance
        if (dist < cutoff_distance) {
            for (int k = 0; k < 3; k++) {
                force[k] += -0.1 * delta_pos[k];
            }
        }
    }

    // Write the force back to the global memory
    for (int k = 0; k < 3; k++) {
        forces[i * 3 + k] = force[k];
    }
}
''', 'compute_forces')


class GPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt

        # Initialize random positions, velocities, and masses on the GPU
        self.positions = cp.random.rand(num_bodies, 3).astype(cp.float64) * 1000.0
        self.velocities = cp.zeros((num_bodies, 3), dtype=cp.float64)
        self.masses = cp.random.rand(num_bodies).astype(cp.float64) * 1e24
        self.forces = cp.zeros((num_bodies, 3), dtype=cp.float64)

    def compute_forces(self):
        # Flatten arrays for the kernel
        positions_flat = self.positions.ravel()
        velocities_flat = self.velocities.ravel()
        forces_flat = self.forces.ravel()

        block_size = 256
        grid_size = (self.num_bodies + block_size - 1) // block_size

        # Launch the custom CUDA kernel, passing G as an argument
        force_kernel((grid_size,), (block_size,), (positions_flat, velocities_flat, self.masses, forces_flat, self.num_bodies, self.cutoff_distance, G))

    def update(self):
        # Compute forces on all bodies
        self.compute_forces()

        # Update velocities and positions
        self.velocities += self.forces / self.masses[:, cp.newaxis] * self.dt
        self.positions += self.velocities * self.dt

    def simulate(self, num_steps):
        start_time = time.time()

        for step in range(num_steps):
            self.update()

        end_time = time.time()
        return end_time - start_time


# Benchmark the simulation to see how many bodies can be simulated at 60 FPS
def benchmark_simulation(num_bodies, cutoff_distance, duration=10):
    sim = GPUNBodySimulation(num_bodies, cutoff_distance)

    # Assume we need to run for 60 FPS for `duration` seconds
    num_steps = int(60 * duration)

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
    if fps < 60:
        print(f"Cannot simulate {num_bodies} bodies at 60 FPS. Stopping.")
        break
