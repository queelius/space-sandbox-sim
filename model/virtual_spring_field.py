from typing import Callable
from model.body import Body
from model.springs import Springs
from events.event_bus import EventBus

def generate_virtual_spring_field(
    event_bus: EventBus,
    distance_threshold: float,
    relative_speed_threshold: float,
    stiffness: float,
    damping: float,
    break_force: float,
    break_distance_factor: float) -> Callable[[list[tuple[Body, Body]],
                                               Springs], int]:
    """

    Generate a function that connects two bodies with a spring if they are too
    close and have a relative velocity below a certain threshold.

    Parameters:
    -----------
    distance_threshold : float
        The maximum distance between two bodies to form a spring.

    relative_speed_threshold : float
        The maximum relative speed between two bodies to form a spring.

    stiffness : float
        The stiffness of the spring.

    damping : float
        The damping of the spring.

    break_force : float
        The force at which the spring breaks.

    break_distance_factor : float
        The factor of the equilibrium distance at which the spring breaks.

    Returns:
    --------
    Callable[[list[tuple[Body, Body]], Springs], int]
        A function that connects two bodies with a spring if they are too close.

        Parameters:
        -----------
        nearest_neighbors : list[tuple[Body, Body]]
            A list of tuples of bodies that are nearest neighbors.
        springs : Springs
            The springs object that manages the springs between bodies.

        Returns:
        --------
        int
            The number of connections made.
    """

    def connector(
            neighbors: list[tuple[Body, Body]],                            
            springs: Springs) -> int:
        
        connections_made: int = 0  

        for body1, body2 in neighbors:
            if springs.connected(body1, body2):
                continue
            
            delta_pos = body2.pos - body1.pos
            dist = delta_pos.length() - body1.radius - body2.radius
            if dist > distance_threshold:                
                continue

            rel_vel = body2.vel - body1.vel
            rel_speed = rel_vel.length()
            if rel_speed > relative_speed_threshold:
                continue

            # event_bus.publish("virtual_spring_connected", {
            #     "body1": body1,
            #     "body2": body2,
            #     "distance": dist,
            #     "relative_velocity": rel_vel,
            #     "relative_speed": rel_speed
            # })


            connections_made += 1
            springs.link(
                body1=body1,
                body2=body2,
                stiffness=stiffness,
                damping=damping,
                equilibrium=delta_pos.length(),
                break_distance_factor=break_distance_factor,
                break_force=break_force)
                    
        return connections_made

    return connector
