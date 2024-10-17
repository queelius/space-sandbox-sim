from model.body import Body
from model.body_list import BodyList
import networkx as nx
import utils.const as const
from audio.audio_manager import AudioManager
from typing import Callable
from model.composite_body import CompositeBody
from events.event_bus import EventBus

spring_tuple = tuple[Body, Body, float, float, float, float]

class Spring:

    BODY1_IDX = 0
    BODY2_IDX = 1
    STIFFNESS_IDX = 2
    DAMPING_IDX = 3
    EQUILIBRIUM_IDX = 4
    BREAK_FORCE_IDX = 5

    MAX_SPRING_FORCE = 1e6
    
    @staticmethod
    def body1(spring: spring_tuple) -> Body:
        return spring[Spring.BODY1_IDX]

    @staticmethod
    def body2(spring: spring_tuple) -> Body:
        return spring[Spring.BODY2_IDX]

    @staticmethod
    def stiffness(spring: spring_tuple) -> float:
        return spring[Spring.STIFFNESS_IDX]

    @staticmethod
    def damping(spring: spring_tuple) -> float:
        return spring[Spring.DAMPING_IDX]

    @staticmethod
    def equilibrium(spring: spring_tuple) -> float:
        return spring[Spring.EQUILIBRIUM_IDX]

    @staticmethod
    def break_force(spring: spring_tuple) -> float:
        return spring[Spring.BREAK_FORCE_IDX]
        
    @staticmethod
    def compute_force(spring: spring_tuple):

        body1, body2, stiff, damp, equi, break_force = spring
        
        d = body1.pos - body2.pos
        l = d.length()
        if l < 1e-3:
            d = d.normalize() * 1e-3
            l = 1e-3
        f = stiff * (l - equi) * d.normalize()
        f -= damp * (body1.vel - body2.vel)

        f_mag = f.length()
        if f_mag > break_force:
            return None
        
        if f_mag > Spring.MAX_SPRING_FORCE:
            f = f.normalize() * Spring.MAX_SPRING_FORCE

        return f

class Springs:
    """
    A class to represent springs between bodies. This may be used
    to simulate soft bodies or other systems where bodies are connected by
    some kind of attachment.
    """
    def __init__(self,
                 bodies: BodyList,
                 springs: list[tuple[Body, Body, float, float, float, float]],
                 event_bus: EventBus):
        """
        Initialize the Springs object with a list of bodies and a list of
        springs.

        A spring is a tuple given by:
            [body1, body2, k, damping, equilibrium, break_force]
        """
        self.springs = springs
        self.bodies = bodies
        self.event_bus = event_bus

    def link(self,
             body1: Body,
             body2: Body,
             stiffness: float = const.SPRING_STIFFNESS,
             damping: float = const.DAMPING,
             equilibrium: float = None,
             break_force: float = const.SPRING_BREAK_FORCE):
        """
        Link two bodies with a spring.

        If equilibrium is None, it is set to the distance between the two bodies.
        """
        if equilibrium is None:
            equilibrium = (body2.pos - body1.pos).length()

        self.springs.append((body1, body2, stiffness, damping, equilibrium, break_force))

    def unlink(self, body1: Body, body2: Body):
        for spring in self.springs:
            if spring[0] is body1 and spring[1] is body2:
                self.springs.remove(spring)

    def __iter__(self):
        return iter(self.springs)

    def find_composite_bodies(self,
                              pred: Callable[[tuple[Body, Body, float, float, float, float]], bool] = lambda x: True) -> list[CompositeBody]:
        """
        Find spring-connected bodies that satisfy a spring predicate.

        A predicate is a function that takes a Spring tuple:

            [body1, body2, k, damping, equilibrium, break_force]

        and return True if the spring satisfies the criteria of considering
        the two bodies a (part of) the composite body.
        """
        # treat springs as undirected edges in a graph
        G = nx.Graph()
        # [body1, body2, k, damping, equilibrium, break_force]
        for spring in self.springs:
            if pred(spring):
                G.add_edge(spring[0], spring[1], spring=spring)

        # find connected components
        comps = list(nx.connected_components(G))
        composites = []
        for comp in comps:
            if len(comp) > 1:
                composites.append(CompositeBody(list(comp)))
                
        return composites
    
    def connected(self, body1: Body, body2: Body) -> bool:
        for s in self.springs:
            if body1 is s[0] and body2 is s[1]:
                return True
        return False

    def update(self):
        remove_list = []
        
        for s in self.springs:
            if s[0] not in self.bodies or s[1] not in self.bodies:
                remove_list.append(s)
                continue

            b1, b2, stiff, damp, equi, break_force = s
            d = b2.pos - b1.pos
            l = d.length()
            if l < 1e-2:
                continue
            f = stiff * (l - equi) * d.normalize()
            f -= damp * (b1.vel - b2.vel)

            if f.length() > break_force:
                self.event_bus.publish(
                    'spring_break',
                    {'source_pos': lambda: (b1.pos + b2.pos) / 2,
                     'delay': 0.0})
                remove_list.append(s)
            else:
                b1.add_force(f)
                b2.add_force(-f)

        for s in remove_list:
            self.springs.remove(s)


