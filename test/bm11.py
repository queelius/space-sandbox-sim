import cupy as cp
import numpy as np
import time

# Gravitational constant in single precision
G = cp.float32(6.67430e-11)

# Optimized CUDA kernel using shared memory and single precision
optimized_kernel = cp.RawKernel(r'''
extern "C" __global__
void compute_and_update_optimized(float* positions, float* velocities, float* masses, int num_bodies, float cutoff_distance, float G, float dt) {
    extern __shared__ float shared_positions[];
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= num_bodies) return;
    
    // Load own position and mass
    float pos_i_x = positions[i * 3 + 0];
    float pos_i_y = positions[i * 3 + 1];
    float pos_i_z = positions[i * 3 + 2];
    float mass_i = masses[i];
    
    float force_x = 0.0f;
    float force_y = 0.0f;
    float force_z = 0.0f;
    
    // Loop over tiles
    for (int tile = 0; tile < (num_bodies + blockDim.x - 1) / blockDim.x; tile++) {
        int j = tile * blockDim.x + threadIdx.x;
        if (j < num_bodies) {
            shared_positions[threadIdx.x * 3 + 0] = positions[j * 3 + 0];
            shared_positions[threadIdx.x * 3 + 1] = positions[j * 3 + 1];
            shared_positions[threadIdx.x * 3 + 2] = positions[j * 3 + 2];
        } else {
            shared_positions[threadIdx.x * 3 + 0] = 0.0f;
            shared_positions[threadIdx.x * 3 + 1] = 0.0f;
            shared_positions[threadIdx.x * 3 + 2] = 0.0f;
        }
        __syncthreads();
        
        // Compute forces
        for (int j_local = 0; j_local < blockDim.x && (tile * blockDim.x + j_local) < num_bodies; j_local++) {
            int j_global = tile * blockDim.x + j_local;
            if (i == j_global) continue;
            
            float dx = shared_positions[j_local * 3 + 0] - pos_i_x;
            float dy = shared_positions[j_local * 3 + 1] - pos_i_y;
            float dz = shared_positions[j_local * 3 + 2] - pos_i_z;
            
            float dist_sq = dx * dx + dy * dy + dz * dz + 1e-10f;
            float dist = sqrtf(dist_sq);
            float inv_dist_cube = 1.0f / (dist_sq * dist);
            
            float mass_j = masses[j_global];
            float force_scalar = G * mass_i * mass_j * inv_dist_cube;
            force_x += force_scalar * dx;
            force_y += force_scalar * dy;
            force_z += force_scalar * dz;
            
            // Repulsive force
            if (dist < cutoff_distance) {
                force_x += -0.1f * dx;
                force_y += -0.1f * dy;
                force_z += -0.1f * dz;
            }
        }
        __syncthreads();
    }
    
    // Update velocity and position
    velocities[i * 3 + 0] += (force_x / mass_i) * dt;
    velocities[i * 3 + 1] += (force_y / mass_i) * dt;
    velocities[i * 3 + 2] += (force_z / mass_i) * dt;
    
    positions[i * 3 + 0] += velocities[i * 3 + 0] * dt;
    positions[i * 3 + 1] += velocities[i * 3 + 1] * dt;
    positions[i * 3 + 2] += velocities[i * 3 + 2] * dt;
}
''', 'compute_and_update_optimized')

class OptimizedGPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt

        # Initialize with single precision on GPU
        self.positions = cp.random.rand(num_bodies, 3).astype(cp.float32) * 1000.0
        self.velocities = cp.zeros((num_bodies, 3), dtype=cp.float32)
        self.masses = cp.random.rand(num_bodies).astype(cp.float32) * 1e24

        # Allocate pinned memory for host data
        self.host_positions = cp.cuda.alloc_pinned_memory(self.positions.nbytes)
        self.host_velocities = cp.cuda.alloc_pinned_memory(self.velocities.nbytes)
        self.host_masses = cp.cuda.alloc_pinned_memory(self.masses.nbytes)

        # Create a CUDA stream for asynchronous operations
        self.stream = cp.cuda.Stream(non_blocking=True)

    def step(self):
        # Flatten arrays for the kernel
        positions_flat = self.positions.ravel()
        velocities_flat = self.velocities.ravel()

        block_size = 256
        grid_size = (self.num_bodies + block_size - 1) // block_size
        shared_mem_size = block_size * 3 * 4  # 3 floats per body

        # Launch the optimized kernel on the specified stream
        optimized_kernel((grid_size,), (block_size,), 
                        (positions_flat, velocities_flat, self.masses, self.num_bodies, 
                         self.cutoff_distance, G, self.dt), 
                        shared_mem=shared_mem_size, stream=self.stream.ptr)

        # Asynchronously copy data back to the host
        # Use memoryviews to avoid unnecessary data duplication
        self.stream.wait()  # Ensure the kernel has completed

        # Transfer positions
        cp.cuda.runtime.memcpyAsync(
            self.host_positions.ptr, 
            self.positions.data.ptr, 
            self.positions.nbytes, 
            cp.cuda.runtime.cudaMemcpyKind.cudaMemcpyDeviceToHost, 
            self.stream.ptr
        )

        # Transfer velocities
        cp.cuda.runtime.memcpyAsync(
            self.host_velocities.ptr, 
            self.velocities.data.ptr, 
            self.velocities.nbytes, 
            cp.cuda.runtime.cudaMemcpyKind.cudaMemcpyDeviceToHost, 
            self.stream.ptr
        )

        # Transfer masses (if masses are changing; if not, you can skip this)
        cp.cuda.runtime.memcpyAsync(
            self.host_masses.ptr, 
            self.masses.data.ptr, 
            self.masses.nbytes, 
            cp.cuda.runtime.cudaMemcpyKind.cudaMemcpyDeviceToHost, 
            self.stream.ptr
        )

        # Synchronize the stream to ensure all transfers are complete
        self.stream.synchronize()

    def get_cpu_data(self):
        # Convert pinned memory to NumPy arrays for CPU access
        positions_cpu = np.frombuffer(self.host_positions, dtype=np.float32).reshape((self.num_bodies, 3))
        velocities_cpu = np.frombuffer(self.host_velocities, dtype=np.float32).reshape((self.num_bodies, 3))
        masses_cpu = np.frombuffer(self.host_masses, dtype=np.float32)
        return positions_cpu, velocities_cpu, masses_cpu

    def simulate(self, num_steps, visualize_callback=None):
        start_time = time.time()

        for step_num in range(num_steps):
            self.step()

            # Retrieve CPU data after each step
            positions_cpu, velocities_cpu, masses_cpu = self.get_cpu_data()

            # Optionally, process or visualize the data here
            if visualize_callback:
                visualize_callback(positions_cpu, velocities_cpu, masses_cpu)

        end_time = time.time()
        elapsed_time = end_time - start_time
        avg_fps = num_steps / elapsed_time

        print(f"[Optimized] Simulated {self.num_bodies} bodies for {elapsed_time:.2f} seconds.")
        print(f"[Optimized] Average FPS: {avg_fps:.2f}")

        return avg_fps
