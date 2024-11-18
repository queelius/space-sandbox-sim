from utils.circle_tools import CircleTools

class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def intersect(self, other: "Circle") -> bool:
        return CircleTools.intersect(self.radius, other.radius, (self.center - other.center).length())
    
    def intersection_area(self, other: "Circle") -> float:
        return CircleTools.intersection_area(self.radius, other.radius, (self.center - other.center).length())
    
    def chord_length(self, other: "Circle") -> float:
        return CircleTools.chord_length(self.radius, other.radius, (self.center - other.center).length())

    def penetration_depth(self, other: "Circle") -> float:
        return CircleTools.penetration_depth(self.radius, other.radius, (self.center - other.center).length())        
    
    def centroid(self):
        return self.center
    
    def area(self):
        return CircleTools.area(self.radius)
    
    def perimeter(self):
        return CircleTools.perimeter(self.radius)
    
    def scale(self, factor):
        self.radius *= factor

    def translate(self, dx, dy):
        self.center += (dx, dy)

    def __contains__(self, point):
        return CircleTools.point_inside(point, self.center, self.radius)

    def __repr__(self):
        return f"Circle(pos={self.center}, radius={self.radius})"
    
    def __str__(self):
        return self.__repr__()
    

