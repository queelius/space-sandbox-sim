from pygame.math import Vector2 as vec2
from utils.utils import cross
from model.circle import Circle
import math

class ConvexHull:
    def __init__(self, points: list[vec2]):
        """
        A class to represent a convex hull of a list of bodies.
        """
        self.convex_hull = ConvexHull.compute_convex_hull(points)

    def __contains__(self, point: vec2) -> bool:
        """
        Determine if a point is inside the convex hull.

        Parameters:
        -----------
        point : vec2
            The point to check.

        Returns:
        --------
        is_inside : bool
            True if the point is inside the convex hull
        """

        # Check if the point is on the hull
        if point in self.convex_hull:
            return True

        # Check if the point is inside the hull
        for i in range(len(self.convex_hull)):
            p1 = self.convex_hull[i]
            p2 = self.convex_hull[(i + 1) % len(self.convex_hull)]
            if cross(p1, p2, point) > 0:
                return False

        return True

    @staticmethod
    def compute_convex_hull(points: list[vec2]) -> list[vec2]:
        """
        Calculate the convex hull of a list of points.
        """
        points = sorted(points, key=lambda p: (p.x, p.y))
        if len(points) <= 1:
            return points

        # Lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        # Upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        # Remove the last point of each half because it's repeated at the beginning of the other half
        return lower[:-1] + upper[:-1]
        
    @property
    def area(self) -> float:
        """
        Calculate the area of the convex hull.
        """
        area: float = 0
        for i in range(len(self.convex_hull)):
            p1 = self.convex_hull[i]
            p2 = self.convex_hull[(i + 1) % len(self.convex_hull)]
            area += p1.cross(p2) / 2

        return abs(area)    

    @area.setter
    def area(self, value: float) -> None:
        """
        Adjust the area of the convex hull by scaling it.
        """
        current_area = self.area
        scale = math.sqrt(value / current_area)
        self *= scale
    
    def perimeter(self) -> float:
        """
        Calculate the perimeter of the convex hull.

        Returns:
        --------
        float
            The perimeter of the convex hull.
        """
        perimeter: float = 0
        for i in range(len(self.convex_hull)):
            p1 = self.convex_hull[i]
            p2 = self.convex_hull[(i + 1) % len(self.convex_hull)]
            perimeter += (p1 - p2).length()

        return perimeter
    
    @property
    def centroid(self) -> vec2:
        """
        Calculate the centroid of the convex hull.

        Returns:
        --------
        vec2
            The centroid of the convex hull.
        """
        centroid = vec2(0, 0)
        for i in range(len(self.convex_hull)):
            p1 = self.convex_hull[i]
            p2 = self.convex_hull[(i + 1) % len(self.convex_hull)]
            cross_product = p1.cross(p2)
            centroid += (p1 + p2) * cross_product

        return centroid / (6 * self.area)
    
    @centroid.setter
    def centroid(self, value: vec2) -> None:
        """
        Adjust the centroid of the convex hull by translating it.

        Parameters:
        -----------
        value : vec2
            The new centroid of the convex hull.
        """
        current_centroid = self.centroid
        translation = value - current_centroid
        self += translation

    def bounding_radius(self) -> float:
        """
        Calculate the bounding radius of the convex hull.

        Returns:
        --------
        float
            The bounding radius of the convex hull.
        """
        return max((point - self.centroid).length() for point in self.convex_hull)
    
    def bounding_circle(self) -> Circle:
        """
        Calculate the bounding circle of the convex hull.

        Returns:
        --------
        tuple[vec2, float]
            The center and radius of the bounding circle.
        """
        return Circle(self.centroid, self.bounding_radius())
    
    def bounding_box(self) -> tuple[vec2, vec2]:
        """
        Calculate the bounding box of the convex hull.

        Returns:
        --------
        tuple[vec2, vec2]
            The minimum and maximum points of the bounding box.
        """
        min_x = min(self.convex_hull, key=lambda p: p.x).x
        max_x = max(self.convex_hull, key=lambda p: p.x).x
        min_y = min(self.convex_hull, key=lambda p: p.y).y
        max_y = max(self.convex_hull, key=lambda p: p.y).y
        return vec2(min_x, min_y), vec2(max_x, max_y)
    
    def __iter__(self):
        return iter(self.convex_hull)
    
    def __len__(self):
        return len(self.convex_hull)
    
    def __getitem__(self, index: int) -> vec2:
        return self.convex_hull[index]
    
    def __str__(self) -> str:
        return f"ConvexHull(num_points={len(self.convex_hull)})"
    
    def __repr__(self) -> str:
        return f"ConvexHull({self.convex_hull})"
    
    def __eq__(self, other) -> bool:
        return self.convex_hull == other.convex_hull
    
    def __ne__(self, other) -> bool:
        return self.convex_hull != other.convex_hull
    
    def __lt__(self, other) -> bool:
        return self.area < other.area
    
    def __le__(self, other) -> bool:
        return self.area <= other.area
    
    def __gt__(self, other) -> bool:
        return self.area > other.area
    
    def __ge__(self, other) -> bool:
        return self.area >= other.area
    
    def __add__(self, other) -> 'ConvexHull':
        """
        Combine two convex hulls.

        Parameters:
        -----------
        other : ConvexHull
            The other convex hull to combine with this one.

        Returns:
        --------
        ConvexHull
            The combined convex hull.
        """
        return ConvexHull(self.convex_hull + other.convex_hull)
    
    def __sub__(self, other) -> 'ConvexHull':
        """
        Subtract one convex hull from another.

        Parameters:
        -----------
        other : ConvexHull
            The convex hull to subtract from this one.

        Returns:
        --------
        ConvexHull
            The convex hull resulting from the subtraction.
        """
        return ConvexHull([point for point in self.convex_hull if point not in other.convex_hull])
    
    def __mul__(self, scalar: float) -> 'ConvexHull':
        """
        Scale the convex hull by a scalar.

        Parameters:
        -----------
        scalar : float
            The scalar to multiply the convex hull by.

        Returns:
        --------
        ConvexHull
            The scaled convex hull.
        """
        return ConvexHull([point * scalar for point in self.convex_hull])
