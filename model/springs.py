from model.body import Body
from model.body_list import BodyList
import networkx as nx
from pygame.math import Vector2 as vec2

class Springs:
    """
    A class to represent springs between bodies. This may be used
    to simulate soft bodies or other systems where bodies are connected by
    some kind of attachment.
    """
    def __init__(self,
                 bodies: BodyList,
                 springs: list[tuple[Body, Body, float, float, float, float]]):
        """
        Initialize the Springs object with a list of bodies and a list of
        springs.

        A spring is a tuple given by:
            [body1, body2, k, damping, equilibrium, break_force]
        """
        self.springs = springs
        self.bodies = bodies

    def link(self, body1: Body, body2: Body, k: float, damping: float, equilibrium: float, break_force: float):
        self.springs.append((body1, body2, k, damping, equilibrium, break_force))

    def unlink(self, body1: Body, body2: Body):
        for spring in self.springs:
            if spring[0] is body1 and spring[1] is body2:
                self.springs.remove(spring)

    def find_clusters(self):
        """
        Find clusters of spring-connected bodies.
        """
        # treat springs as undirected edges in a graph

        G = nx.Graph()
        # [body1, body2, k, damping, equilibrium, break_force]
        for body1, body2, _, _, _, _ in self.springs:
            G.add_edge(body1, body2)

        comps = nx.connected_components(G)


    def compute_force(self, spring: tuple[Body, Body, float, float, float, float]) -> vec2:
        """
        Helper function to compute the force between two bodies connected by a spring.
        """

        body1, body2, k, damping, equilibrium, _ = spring
        d = body2.pos - body1.pos
        l = d.length()
        f = k * (l - equilibrium) * d.normalize()
        f -= damping * (body1.velocity - body2.velocity)
        return f

    def update(self):
        remove_list = []
        
        for s in self.springs:
            if s[0] not in self.bodies or s[1] not in self.bodies:
                remove_list.append(s)
                continue

            body1, body2, stiffness, damping, equilibrium, break_force = s
            d = body2.pos - body1.pos
            l = d.length()
            f = stiffness * (l - equilibrium) * d.normalize()
            f -= damping * (body1.velocity - body2.velocity)
            if l > break_force:
                remove_list.append((body1, body2))
            body1.add_force(f)
            body2.add_force(-f)

        for s in remove_list:
            self.springs.remove(s)


