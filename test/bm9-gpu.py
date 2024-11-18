import cupy as cp
import numpy as np
import time

# Gravitational constant
G = 6.67430e-11

# Combined CUDA kernel for force computation and position/velocity update
combined_kernel = cp.RawKernel(r'''
extern "C" __global__
void compute_and_update(double* positions, double* velocities, double* masses, int num_bodies, double cutoff_distance, double G, double dt) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= num_bodies) return;
    
    double force_i[3] = {0.0, 0.0, 0.0};
    double pos_i[3];
    double mass_i = masses[i];

    // Load position of body i
    pos_i[0] = positions[i * 3 + 0];
    pos_i[1] = positions[i * 3 + 1];
    pos_i[2] = positions[i * 3 + 2];

    for (int j = 0; j < num_bodies; j++) {
        if (i == j) continue;

        double delta_pos[3];
        double pos_j[3];

        // Load position of body j
        pos_j[0] = positions[j * 3 + 0];
        pos_j[1] = positions[j * 3 + 1];
        pos_j[2] = positions[j * 3 + 2];

        // Calculate the difference in positions
        delta_pos[0] = pos_j[0] - pos_i[0];
        delta_pos[1] = pos_j[1] - pos_i[1];
        delta_pos[2] = pos_j[2] - pos_i[2];

        // Calculate the squared distance
        double dist_sq = delta_pos[0] * delta_pos[0] + delta_pos[1] * delta_pos[1] + delta_pos[2] * delta_pos[2] + 1e-10;
        double dist = sqrt(dist_sq);
        double inv_dist_cube = 1.0 / (dist_sq * dist);

        // Gravitational force
        double mass_j = masses[j];
        double force_scalar = G * mass_i * mass_j * inv_dist_cube;
        force_i[0] += force_scalar * delta_pos[0];
        force_i[1] += force_scalar * delta_pos[1];
        force_i[2] += force_scalar * delta_pos[2];

        // Apply repulsive force if within cutoff distance
        if (dist < cutoff_distance) {
            force_i[0] += -0.1 * delta_pos[0];
            force_i[1] += -0.1 * delta_pos[1];
            force_i[2] += -0.1 * delta_pos[2];
        }
    }

    // Update velocity and position of body i
    velocities[i * 3 + 0] += (force_i[0] / mass_i) * dt;
    velocities[i * 3 + 1] += (force_i[1] / mass_i) * dt;
    velocities[i * 3 + 2] += (force_i[2] / mass_i) * dt;

    positions[i * 3 + 0] += velocities[i * 3 + 0] * dt;
    positions[i * 3 + 1] += velocities[i * 3 + 1] * dt;
    positions[i * 3 + 2] += velocities[i * 3 + 2] * dt;
}
''', 'compute_and_update')


class GPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt

        self.count = 0

        # Initialize random positions, velocities, and masses on the GPU
        self.positions = cp.random.rand(num_bodies, 3).astype(cp.float64) * 1000.0
        self.velocities = cp.zeros((num_bodies, 3), dtype=cp.float64)
        self.masses = cp.random.rand(num_bodies).astype(cp.float64) * 1e24

    def step(self):
        # Flatten arrays for the kernel
        positions_flat = self.positions.ravel()
        velocities_flat = self.velocities.ravel()

        block_size = 128
        grid_size = (self.num_bodies + block_size - 1) // block_size

        # Launch the combined kernel
        combined_kernel((grid_size,), (block_size,), 
                        (positions_flat, velocities_flat, self.masses, self.num_bodies, self.cutoff_distance, G, self.dt))
        
    def print_fastest_body(self, velocities):
        max_speed = 0.0
        fastest_body = -1

        for i in range(self.num_bodies):
            speed = velocities[i, 0] ** 2 + velocities[i, 1] ** 2 + velocities[i, 2] ** 2
            if speed > max_speed:
                max_speed = speed
                fastest_body = i

        self.count += 1
        if self.count % 200 == 0:
            print(f"Step {self.count}: body {fastest_body} w/speed {max_speed}")

    def simulate(self, num_steps):
        start_time = time.time()

        for step in range(num_steps):
            self.step()
            #xs = cp.asnumpy(self.positions)  # Print the first 5 positions after update
            ys = cp.asnumpy(self.velocities)  # Print the first 5 velocities after update
            #zs = cp.asnumpy(self.masses)  # Print the first 5 masses
            self.print_fastest_body(ys)

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
