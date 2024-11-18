import math
from collections import defaultdict

class SpatialHash:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.hash_map = defaultdict(list)

    def _hash(self, x, y):
        """Hash function that maps coordinates to grid cells."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, obj, x, y):
        """Insert an object into the spatial hash."""
        cell = self._hash(x, y)
        self.hash_map[cell].append((obj, (x, y)))

    def remove(self, obj, x, y):
        """Remove an object from the spatial hash."""
        cell = self._hash(x, y)
        self.hash_map[cell].remove((obj, (x, y)))
        if not self.hash_map[cell]:  # If cell is empty, remove it from the map
            del self.hash_map[cell]

    def query(self, x, y, radius):
        """Find all objects within a given radius of (x, y)."""
        nearby_objects = []
        cell_radius = math.ceil(radius / self.cell_size)
        center_cell = self._hash(x, y)
        
        for i in range(center_cell[0] - cell_radius, center_cell[0] + cell_radius + 1):
            for j in range(center_cell[1] - cell_radius, center_cell[1] + cell_radius + 1):
                cell = (i, j)
                if cell in self.hash_map:
                    for obj, (ox, oy) in self.hash_map[cell]:
                        if (ox - x) ** 2 + (oy - y) ** 2 <= radius ** 2:
                            nearby_objects.append(obj)
        return nearby_objects

    def update(self, obj, old_x, old_y, new_x, new_y):
        """Update the position of an object in the spatial hash."""
        self.remove(obj, old_x, old_y)
        self.insert(obj, new_x, new_y)

# Example usage
if __name__ == "__main__":
    # Create a spatial hash with cell size of 10 units
    spatial_hash = SpatialHash(10)

    # Insert some objects
    spatial_hash.insert("Object 1", 5, 5)
    spatial_hash.insert("Object 2", 15, 15)
    spatial_hash.insert("Object 3", 25, 25)

    # Query nearby objects within a radius of 10 units from (10, 10)
    nearby = spatial_hash.query(10, 10, 10)
    print("Nearby objects:", nearby)

    # Update object position
    spatial_hash.update("Object 1", 5, 5, 12, 12)
    nearby = spatial_hash.query(10, 10, 10)
    print("Nearby objects after update:", nearby)
