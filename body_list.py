from body import Body

class BodyList:
    def __init__(self, max_bodies: int):
        self.bodies : list[Body] = [None] * max_bodies
        self.num_bodies = 0
        self.max_bodies = max_bodies

    def __getitem__(self, index: int) -> Body:
        return self.bodies[index]
    
    def __setitem__(self, index: int, value: Body) -> None:
        self.bodies[index] = value

    def add(self, value: Body) -> None:
        #if self.num_bodies >= self.max_bodies:
        #    raise ValueError("BodyList is full")
        self.bodies[self.num_bodies] = value
        self.num_bodies += 1

    def remove(self, index) -> None:
        self.bodies[index] = self.bodies[self.num_bodies - 1]
        self.num_bodies -= 1

    def remove_item(self, item: Body) -> None:
        index = self.bodies.index(item)
        self.remove(index)

    def clear(self) -> None:
        self.num_bodies = 0

    def __iter__(self):
        for i in range(self.num_bodies):
            yield self.bodies[i]
    
    def __len__(self) -> int:
        return self.num_bodies
    
    def __contains__(self, item: Body) -> bool:
        for i in range(self.num_bodies):
            if self.bodies[i] == item:
                return True
        return False
    
    def index(self, item: Body) -> int:
        for i in range(self.num_bodies):
            if self.bodies[i] is item:
                return i
        return 0
    
    def __str__(self) -> str:
        return f"BodyList(num_bodies={self.num_bodies})"