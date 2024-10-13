from model.springs import Springs
import heapq
from model.body import Body

def create_spring_mesh(springs : Springs,
                       composite: list[Body],
                       stiffness: float,
                       damping: float,
                       break_force: float,
                       k: int = 3) -> None:
    """
    Create a spring mesh connecting each body to its k-nearest neighbors.
    
    Parameters:
    -----------
    springs : Springs
        The Springs object to add the springs to. This contains *all* the
        springs in the simulation, typically, and it also has a reference to
        all the bodies in the simulation.

    composite : list[Body]
        The list of bodies to connect with springs.

    stiffness : float
        The spring stiffness constant.

    damping : float
        The damping constant.

    break_force : float
        The force at which the spring breaks.

    k : int
        The number of nearest neighbors to connect each body to.
    """

    num_bodies = len(composite)
    dist2 = []
    for i in range(num_bodies):
        for j in range(i + 1, num_bodies):
            dist2.append((composite[i].pos - composite[j].pos).length_squared())
    
    # Use a min-heap to find the k-nearest neighbors for each body
    for i in range(num_bodies):
        neighbors = []
        for j in range(num_bodies):
            if i != j:
                d2 = (composite[i].pos - composite[j].pos).length_squared()
                heapq.heappush(neighbors, (d2, j))
        
        # Link the k-nearest neighbors
        for _ in range(min(k, len(neighbors))):
            _, neighbor_idx = heapq.heappop(neighbors)
            springs.link(body1=composite[i],
                         body2=composite[neighbor_idx],
                         stiffness=stiffness,
                         damping=damping,
                         equilibrium=None,
                         break_force=break_force)