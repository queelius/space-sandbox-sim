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
    BREAK_DISTANCE_FACTOR_IDX = 5
    BREAK_FORCE_IDX = 6    

    MAX_SPRING_FORCE = 1e9
    DEFAULT_BREAK_DISTANCE_FACTOR = 1.5
    DEFAULT_BREAK_FORCE = 1e7
    DEFAULT_STIFFNESS = 1e6
    DEFAULT_DAMPING = 1e2
    
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
    def break_distance_factor(spring: spring_tuple) -> float:
        return spring[Spring.BREAK_DISTANCE_FACTOR_IDX]
        
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
             damping: float = const.SPRING_DAMPING,
             equilibrium: float = None,
             break_distance_factor: float = const.SPRING_BREAK_DISTANCE_FACTOR,
             break_force: float = const.SPRING_BREAK_FORCE) -> None:
        """
        Link two bodies with a spring.

        If equilibrium is None, it is set to the distance between the two bodies.
        """
        if equilibrium is None:
            equilibrium = (body2.pos - body1.pos).length()
        self.springs.append((body1, body2, stiffness, damping, equilibrium, break_distance_factor, break_force))
        # self.event_bus.publish("spring_connected", { "body1": body1,
        #                                             "body2": body2,
        #                                             "stiffness": stiffness,
        #                                             "damping": damping,
        #                                             "equilibrium": equilibrium,
        #                                             "break_distance_factor": break_distance_factor,
        #                                             "break_force": break_force })
        

    def unlink(self, body1: Body, body2: Body):
        for body1, body2, spring in self.springs:
            if spring[0] is body1 and spring[1] is body2:
                self.springs.remove(spring)

    def __iter__(self):
        return iter(self.springs)

    def find_composite_bodies(self,
                              pred: Callable[[tuple[Body, Body, float, float, float, float, float]], bool] = lambda x: True) -> list[CompositeBody]:
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
                G.add_edge(spring[Spring.BODY1_IDX],
                           spring[Spring.BODY2_IDX],
                           spring=spring)

        # find connected components
        comps = list(nx.connected_components(G))
        composites = []
        for comp in comps:
            if len(comp) > 1:
                composites.append(CompositeBody(list(comp)))
                
        return composites
    
    def connected(self, body1: Body, body2: Body) -> bool:
        for b1, b2, _, _, _, _, _ in self.springs:
            if ((body1 is b1 and body2 is b2 or
                (body1 is b2 and body2 is b1))):
                return True
        return False

    def update(self):
        remove_list = []
        
        for s in self.springs:
            b1, b2, stiff, damp, equi, break_distance_factor, break_force = s
            if b1 not in self.bodies or b2 not in self.bodies:
                remove_list.append(s)
                continue            
            d = b2.pos - b1.pos
            l = d.length()
            break_dist = break_distance_factor * equi
            if l > break_dist:
                # self.event_bus.publish(
                #     'spring_break_distance',
                #     {'source_pos': lambda: (b1.pos + b2.pos) / 2,
                #      'body1': b1,
                #      'body2': b2,
                #      'distance': l,
                #      'equilibrium': equi,
                #      'break_distance': break_dist,
                #      'delay': 0.0})
                remove_list.append(s)
                continue

            if l < 1e-3:
                continue

            f = stiff * (l - equi) * d.normalize()
            f -= damp * (b1.vel - b2.vel)

            f_mag = f.length()
            if f_mag > break_force:
                # self.event_bus.publish(
                #     'spring_break_force',
                #     {'source_pos': lambda: (b1.pos + b2.pos) / 2,
                #      'body1': b1,
                #      'body2': b2,
                #      'force_mag': f_mag,
                #      'break_force': break_force,
                #      'delay': 0.0})
                remove_list.append(s)
                continue

            if f_mag > Spring.MAX_SPRING_FORCE:
                f = f.normalize() * Spring.MAX_SPRING_FORCE

            b1.add_force(f)
            b2.add_force(-f)

        for s in remove_list:
            self.springs.remove(s)


