from model.body import Body
from model.body_list import BodyList
from typing import Callable, Optional
from model.condition import Condition
from events.event_bus import EventBus

def generate_spontaneous_body_merging(
        event_bus: EventBus,
        merge_condition: Condition) -> Callable[[BodyList], None]:
    """
    Generate a function that merges bodies that satisfy a given merge condition.

    Parameters:
    -----------
    merge_condition : Condition
        The condition that determines whether two bodies should be merged.

    Returns:
    --------
    Callable[[BodyList], None]
        A function that merges bodies that satisfy the merge condition.

        Parameters:
        -----------
        neighbors : list[tuple[Body, Body]]
            A list of tuples of bodies that are "neighbors" (generally, we
            compute this list using a QuadTree with some distance threshold).
            This may exclude some pairs of bodies that satisfy the merge
            condition, but are not sufficiently close to be neighbors.
        bodies : BodyList
            The list of bodies to merge to in-place if they satisfy the merge
            condition.
    """
    
    def merge(neighbors: list[tuple[Body, Body]],
              bodies: BodyList) -> None:
        for body1, body2 in neighbors:
            if body1 not in bodies or body2 not in bodies:
                continue
            merged_body = merge_condition(body1, body2)
            if merged_body:
                event_bus.publish("merge_bodies", {"body1": body1, "body2": body2 })

    return merge
            
