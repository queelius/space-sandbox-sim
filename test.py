import numpy as np
import cupy as cp
import time

def numpy_test(size):
    # Create large arrays on the CPU
    a = np.random.rand(size, size).astype(np.float32)
    b = np.random.rand(size, size).astype(np.float32)

    # Start timing
    start_time = time.time()
    c = a * b  # Element-wise multiplication
    cp.cuda.Stream.null.synchronize()  # Ensure computation is finished
    end_time = time.time()

    print(f"NumPy (CPU) computation time: {end_time - start_time:.5f} seconds")

def cupy_test(size):
    # Create large arrays on the GPU
    a = cp.random.rand(size, size, dtype=cp.float32)
    b = cp.random.rand(size, size, dtype=cp.float32)

    # Start timing
    start_time = time.time()
    c = a * b  # Element-wise multiplication
    cp.cuda.Stream.null.synchronize()  # Ensure computation is finished
    end_time = time.time()

    print(f"CuPy (GPU) computation time: {end_time - start_time:.5f} seconds")

if __name__ == "__main__":
    size = 10000  # Adjust the size based on your GPU's memory capacity

    print("Running NumPy test...")
    numpy_test(size)

    print("\nRunning CuPy test...")
    cupy_test(size)
