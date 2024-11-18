from math import sqrt, pi, acos
from typing import Tuple

class CircleTools:
    """
    A collection of tools for working with circular shapes.
    """

    @staticmethod
    def point_inside(point: Tuple[float, float], center: Tuple[float, float], radius: float) -> bool:
        """
        Check if a point is inside a circle.

        Parameters:
        -----------
        point : Tuple[float, float]
            The (x, y) coordinates of the point.
        center : Tuple[float, float]
            The (x, y) coordinates of the center of the circle.
        radius : float
            The radius of the circle.

        Returns:
        --------
        bool
            True if the point is inside the circle, False otherwise.
        """
        return (point.x - center.x)**2 + (point.y - center.y)**2 <= radius**2

    @staticmethod
    def intersect(r1: float, r2: float, d: float) -> bool:
        """
        Check if two circles with radii `r1` and `r2` intersect when separated
        by distance `d`.

        Parameters:
        -----------
        r1 : float
            The radius of the first circle.
        r2 : float
            The radius of the second circle.
        d : float
            The distance between the centers of the two circles.

        Returns:
        --------
        bool
            True if the circles overlap, False otherwise.        
        """
        return d < r1 + r2
    
    @staticmethod
    def chord_length(r1: float, r2: float, d: float) -> float:
        """
        Calculate the length of the chord formed by the intersection of two
        circles with radii `r1` and `r2` and centers separated by distance `d`.

        Parameters:
        -----------
        r1 : float
            The radius of the first circle.
        r2 : float
            The radius of the second circle.
        d : float
            The distance between the centers of the two circles.

        Returns:
        --------
        float
            The length of the chord formed by the intersection of the two
            circles.
        """
        # If they do not overlap, return 0
        if r1 + r2 < d:
            return 0

        # If one circle is inside the other, return 0
        if d <= abs(r2 - r1):
            return 0

        # Calculate the length of the chord formed by the intersection
        part = (d**2 + r1**2 - r2**2) / (2 * d)
        return 2 * sqrt(r1**2 - part**2)

    @staticmethod
    def penetration_depth(r1: float, r2: float, d: float) -> float:
        """
        Calculate the penetration depth of two circles with radii `r1` and `r2`
        separated by distance `d`.

        Parameters:
        -----------
        r1 : float
            The radius of the first circle.
        r2 : float
            The radius of the second circle.
        d : float
            The distance between the centers of the two circles.

        Returns:
        --------
        float
            The projected overlap of the two circles along the line connecting
            their centers.        
        """
        return max(0, r1 + r2 - d)

    @staticmethod
    def intersection_area(r1: float, r2: float, d: float) -> float:
        """
        Calculate the area of overlap between two circles with radii `r1` and
        `r2` separated by a distance `d`.

        Parameters:
        -----------
        r1 : float
            The radius of the first circle.
        r2 : float
            The radius of the second circle.
        d : float
            The distance between the centers of the two circles.

        Returns:
        --------
        float
            The area of overlap (interection) between the two circles.        
        """

        # If the circles do not overlap, return 0
        if d >= r1 + r2:
            return 0

        # If one circle is completely inside the other, return the area of the
        # smaller circle
        if d <= abs(r1 - r2):
            return pi * min(r1, r2) ** 2

        # Calculate the area of the overlapping region
        p1 = r1**2 * acos((d**2 + r1**2 - r2**2) / (2 * d * r1))
        p2 = r2**2 * acos((d**2 + r2**2 - r1**2) / (2 * d * r2))
        p3 = 0.5 * sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))

        return p1 + p2 - p3
