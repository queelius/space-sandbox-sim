import utils.const as const
from model.body import Body
from typing import Callable
from utils.circle_tools import CircleTools
from model.condition import Condition

class MergeCondtion:
    """
    Factory class for creating conditions to determine whether two bodies should
    be merged based on different properties.

    Each method returns a `Condition` object that evaluates a specific merge
    condition between two `Body` instances.

    See `model.condition.Condition` for more details on how to compose conditions
    using logical operators.
    """

    @staticmethod
    def intersection_area(area_ratio: float) -> Condition:
        """
        Creates a condition based on the intersection area of two bodies.

        The condition returns `True` if the intersection area between the two
        bodies is greater than `area_ratio` times the minimum area of the two bodies.

        Parameters:
        -----------
        area_ratio : float
            The threshold ratio for the intersection area.

        Returns:
        --------
        Condition
            A condition function for the intersection area.
        """
        return Condition(
            lambda body1, body2: (CircleTools.intersection_area(
                                    r1=body1.radius,
                                    r2=body2.radius,
                                    d=(body1.pos - body2.pos).length()) >
                                  area_ratio * min(body1.area, body2.area)))

    @staticmethod
    def chord_length(length_ratio: float) -> Callable[[Body, Body], bool]:
        """
        Creates a condition based on the chord length of two bodies.

        The condition returns `True` if the chord length between the two
        bodies is greater than `length_ratio` times the minimum radius of
        the two bodies.

        Parameters:
        -----------
        length_ratio : float
            The threshold ratio for the chord length.

        Returns:
        --------
        Callable[[Body, Body], bool]
            A function that determines if two bodies should be merged based on
            the chord length between them.
        """
        return Condition(
            lambda body1, body2: (CircleTools.chord_length(body1, body2) >
                                  length_ratio * min(body1.radius, body2.radius)))
    
    @staticmethod
    def penetration_depth(length_ratio: float) -> Callable[[Body, Body], bool]:
        """
        Creates a condition based on the penetration depth of two bodies.

        The condition returns `True` if the penetration depth between the two
        bodies is greater than `length_ratio` times the minimum radius of
        the two bodies.

        Parameters:
        -----------
        length_ratio : float
            The threshold ratio for the penetration depth.

        Returns:
        --------
        Callable[[Body, Body], bool]
            A function that determines if two bodies should be merged based on
            the penetration depth between them.
        """
        return Condition(
            lambda body1, body2: (CircleTools.penetration_depth(body1, body2) >
                                  length_ratio * min(body1.radius, body2.radius)))
    
    #@staticmethod
    #def color_similarity(color_threshold: float) -> Callable[[Body, Body], bool]:
    #    return (lambda body1, body2:
    #            Color.color_similarity(body1, body2) < color_threshold)

    @staticmethod
    def relative_speed(speed_threshold: float) -> Callable[[Body, Body], bool]:
        """
        Creates a condition based on the speed difference of two bodies.

        The condition returns `True` if the relative speed between the two
        bodies is greater than `speed_threshold`.

        This condition only makes sense in conjunction with other criteria,
        like `intersection_area`, since by itself it does not take into account
        the positions of the bodies. A useful combination is with, say,
        the condition `intersection_area` to merge bodies that are close
        together and are moving quickly relative to each other.

        ```python
        cond1 = BodyMergeCondition.intersection_area(area_ratio=0.5)
        cond2 = BodyMergeCondition.relative_speed(10)
        combined_cond = BodyMergeCondition.and_conditions(cond1, cond2)
        new_body = merge_bodies(body1, body2, merge_condition=combined_cond))
        ```

        Parameters:
        -----------
        speed_threshold : float
            The threshold relative velocity between the two bodies.

        Returns:
        --------
        Callable[[Body, Body], bool]
            A function that determines if two bodies should be merged based on
            the relative velocity between them.
        """
        return Condition(
            lambda body1, body2: ((body1.vel - body2.vel).length() <
                                  speed_threshold))
    
    @staticmethod
    def point_distance(d: float) -> Callable[[Body, Body], bool]:
        """
        Creates a condition based on the distance between the centers of two bodies.

        The condition returns `True` if the distance between the two bodies is less
        than `d`.

        Note: This is different than their actual distance since it does not
              take into account the radii of the bodies. This is primarily
              useful for merging bodies that have no separation between them,
              and indeed may be mostly overlapping.

        Parameters:
        -----------
        d : float
            The threshold distance between the centers of the two bodies.

        Returns:
        --------
        Callable[[Body, Body], bool]
            A function that determines if two bodies should be merged based on
            the distance between their centers.
        """
        return Condition(
            lambda body1, body2: (body1.pos - body2.pos).length() < d)
    
    @staticmethod
    def mass_ratio(ratio: float) -> Callable[[Body, Body], bool]:
        """
        Creates a condition based on the ratio of the masses of two bodies.

        The condition returns `True` if the ratio of the masses of the two bodies
        is less than `ratio`.

        If both bodies have similar masses, then they are less likely to be merged.
        Intuitively, if we have, say, two very massive bodies, then they are less
        likely to be merged since it may be weird, e.g., two planets merging.
        If each of the planets are actually composite bodies composed of many
        smaller bodies, then these smaller bodies may still merge, since the
        merge condition is not composites of bodies, but individual bodies.

        This condition is useful in conjunction with other conditions, like
        `intersection_area`, to merge bodies that are close together and have
        similar masses.

        Parameters:
        -----------
        ratio : float
            The threshold ratio of the masses of the two bodies.

        Returns:
        --------
        Callable[[Body, Body], bool]
            A function that determines if two bodies should be merged based on
            the ratio of their masses.
        """
        return Condition(
            lambda body1, body2: (min(body1.mass, body2.mass) /
                                  max(body1.mass, body2.mass) < ratio))