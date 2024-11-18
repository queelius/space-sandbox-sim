import numpy as np
#import cupy as cp

class QuadTreeNode:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.center_of_mass = None
        self.mass = 0
        self.body = None
        self.children = [None, None, None, None]  # NW, NE, SW, SE

    def is_leaf(self):
        return self.body is not None and all(child is None for child in self.children)


class QuadTree:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.root = QuadTreeNode(x_min, y_min, x_max, y_max)

    def subdivide(self, node):
        # Create four children for this node
        x_mid = (node.x_min + node.x_max) / 2
        y_mid = (node.y_min + node.y_max) / 2

        node.children[0] = QuadTreeNode(node.x_min, y_mid, x_mid, node.y_max)  # NW
        node.children[1] = QuadTreeNode(x_mid, y_mid, node.x_max, node.y_max)  # NE
        node.children[2] = QuadTreeNode(node.x_min, node.y_min, x_mid, y_mid)  # SW
        node.children[3] = QuadTreeNode(x_mid, node.y_min, node.x_max, y_mid)  # SE

    def get_quadrant(self, node, x, y):
        # Determine which quadrant a body belongs to
        x_mid = (node.x_min + node.x_max) / 2
        y_mid = (node.y_min + node.y_max) / 2

        if x <= x_mid and y >= y_mid:
            return 0  # NW
        elif x > x_mid and y >= y_mid:
            return 1  # NE
        elif x <= x_mid and y < y_mid:
            return 2  # SW
        else:
            return 3  # SE
        
    def insert(self, node, body, mass, x, y, depth=0, tolerance=1e-5):
        if node.is_leaf():
            if node.body is None:
                # This node is empty, place the body here
                node.body = body
                node.mass = mass
                node.center_of_mass = (x, y)
            else:
                # Check if the new body is in the same position as the existing body
                if np.isclose(node.center_of_mass[0], x, atol=tolerance) and np.isclose(node.center_of_mass[1], y, atol=tolerance):
                    # Same position, handle degenerate case by adding jitter or stopping subdivision
                    x += tolerance
                    y += tolerance

                # If there's already a body, and depth limit is reached, stop subdividing
                if depth >= self.max_depth:
                    # Stop subdividing and handle bodies in this node
                    if node.bodies is None:
                        node.bodies = [(node.body, node.mass, node.center_of_mass)]
                    node.bodies.append((body, mass, (x, y)))
                else:
                    # Subdivide and reinsert bodies
                    self.subdivide(node)
                    # Re-insert the existing body into one of the children
                    quadrant = self.get_quadrant(node, node.center_of_mass[0], node.center_of_mass[1])
                    if node.children[quadrant] is None:
                        node.children[quadrant] = self.create_new_child(node, quadrant)
                    self.insert(node.children[quadrant], node.body, node.mass, node.center_of_mass[0], node.center_of_mass[1], depth + 1)

                    # Insert the new body
                    quadrant = self.get_quadrant(node, x, y)
                    if node.children[quadrant] is None:
                        node.children[quadrant] = self.create_new_child(node, quadrant)
                    self.insert(node.children[quadrant], body, mass, x, y, depth + 1)
        else:
            # Insert into one of the children quadrants
            quadrant = self.get_quadrant(node, x, y)
            if node.children[quadrant] is None:
                node.children[quadrant] = self.create_new_child(node, quadrant)
            self.insert(node.children[quadrant], body, mass, x, y, depth + 1)

        # Update the mass and center of mass of the current node
        total_mass = node.mass + mass
        node.center_of_mass = (
            (node.center_of_mass[0] * node.mass + x * mass) / total_mass,
            (node.center_of_mass[1] * node.mass + y * mass) / total_mass
        )
        node.mass = total_mass

    def create_new_child(self, node, quadrant):
        # Create a new QuadTreeNode in the correct quadrant
        x_mid = (node.x_min + node.x_max) / 2
        y_mid = (node.y_min + node.y_max) / 2

        if quadrant == 0:  # NW
            return QuadTreeNode(node.x_min, y_mid, x_mid, node.y_max)
        elif quadrant == 1:  # NE
            return QuadTreeNode(x_mid, y_mid, node.x_max, node.y_max)
        elif quadrant == 2:  # SW
            return QuadTreeNode(node.x_min, node.y_min, x_mid, y_mid)
        else:  # SE
            return QuadTreeNode(x_mid, node.y_min, node.x_max, y_mid)

        
    def calculate_force(self, body_x, body_y, body_mass, theta, G):
        return self._calculate_force_recursive(self.root, body_x, body_y, body_mass, theta, G)

    def _calculate_force_recursive(self, node, body_x, body_y, body_mass, theta, G):
        if node.is_leaf() and node.body is None:
            # No force contribution from an empty node
            return np.array([0.0, 0.0])

        dx = node.center_of_mass[0] - body_x
        dy = node.center_of_mass[1] - body_y
        dist_sq = dx * dx + dy * dy
        dist = np.sqrt(dist_sq + 1e-10)  # Avoid division by zero

        # Size of the quadrant
        s = max(node.x_max - node.x_min, node.y_max - node.y_min)

        # If the node is far enough, approximate as a single mass
        if s / dist < theta:
            force_magnitude = G * node.mass * body_mass / (dist_sq + 1e-10)
            force = np.array([force_magnitude * dx / dist, force_magnitude * dy / dist])
            return force

        # Otherwise, recurse into children
        total_force = np.array([0.0, 0.0])
        for child in node.children:
            if child is not None:
                total_force += self._calculate_force_recursive(child, body_x, body_y, body_mass, theta, G)

        return total_force




class GPUNBodySimulation:
    def __init__(self, num_bodies, cutoff_distance, dt=1.0, theta=0.5):
        self.num_bodies = num_bodies
        self.cutoff_distance = cutoff_distance
        self.dt = dt
        self.theta = theta

        # Initialize random positions, velocities, and masses on the GPU
        self.positions = np.random.rand(num_bodies, 2) * 1000.0  # 2D positions for now
        self.velocities = np.zeros((num_bodies, 2))
        self.masses = np.random.rand(num_bodies) * 1e24
        self.forces = np.zeros((num_bodies, 2))

        # Initialize QuadTree
        self.quad_tree = QuadTree(0, 0, 1000, 1000)

    def compute_forces(self, G):
        # Insert bodies into the QuadTree
        self.quad_tree = QuadTree(0, 0, 1000, 1000)
        for i in range(self.num_bodies):
            self.quad_tree.insert(self.quad_tree.root, i, self.masses[i], self.positions[i, 0], self.positions[i, 1])

        # Compute forces using Barnes-Hut
        for i in range(self.num_bodies):
            self.forces[i] = self.quad_tree.calculate_force(self.positions[i, 0], self.positions[i, 1], self.masses[i], self.theta, G)

    def update(self, G):
        # Compute forces on all bodies
        self.compute_forces(G)

        # Update velocities and positions
        self.velocities += self.forces / self.masses[:, np.newaxis] * self.dt
        self.positions += self.velocities * self.dt

    def simulate(self, num_steps, G):
        for step in range(num_steps):
            self.update(G)


# Benchmark the simulation
def benchmark_simulation(num_bodies, cutoff_distance, duration=10):
    sim = GPUNBodySimulation(num_bodies, cutoff_distance)
    G = 6.67430e-11  # Gravitational constant

    num_steps = int(60 * duration)
    sim.simulate(num_steps, G)

    print(f"Simulated {num_bodies} bodies using Barnes-Hut algorithm.")


# Run the benchmark
benchmark_simulation(10000, 50.0)
