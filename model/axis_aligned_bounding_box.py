from model.circle import Circle

class AABB:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def centroid(self):
        return self.width / 2, self.height / 2
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)
    
    def scale(self, factor):
        self.width *= factor
        self.height *= factor

    def translate(self, dx, dy):
        self.width += dx
        self.height += dy

    def bounding_box(self):
        return self
    
    def bounding_radius(self):
        return (self.width ** 2 + self.height ** 2) ** 0.5 / 2
    
    def bounding_circle(self):
        return Circle(self.centroid, self.bounding_radius())
    
    def __contains__(self, point):
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def __repr__(self):
        return f"Box(width={self.width}, height={self.height})"
    
    def __str__(self):
        return self.__repr__()
    
    
