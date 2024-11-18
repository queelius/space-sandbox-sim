from model.body import Body
import numpy as np
from typing import Optional

class BodyList:
    def __init__(self, max_bodies: int):
        self.bodies: np.ndarray = np.empty(max_bodies, dtype=object)
        self.count = 0

    @staticmethod
    def from_list(bodies: list[Body], max_bodies: Optional[int] = None) -> 'BodyList':
        if max_bodies is None:
            max_bodies = len(bodies)
            
        if max_bodies < len(bodies):
            raise ValueError("max_bodies must be greater than or equal to the number of bodies.")
        
        body_list = BodyList(max_bodies)
        for body in bodies:
            body_list.add(body)
        return body_list

    def __getitem__(self, index: int) -> Body:
        return self.bodies[index]
    
    def __setitem__(self, index: int, value: Body) -> None:
        self.bodies[index] = value

    def add(self, value: Body) -> None:
        if self.count < len(self.bodies):
            self.bodies[self.count] = value
            self.count += 1
        else:
            raise IndexError("BodyList is full. Cannot add more bodies.")

    def remove(self, index) -> None:
        if 0 <= index < self.count:
            self.bodies[index:self.count-1] = self.bodies[index+1:self.count]
            self.bodies[self.count-1] = None
            self.count -= 1
        else:
            raise IndexError("Index out of range.")

    @property
    def num_bodies(self) -> int:
        return self.count

    def remove_item(self, item: Body) -> None:
        index = self.index(item)
        self.remove(index)

    def clear(self) -> None:
        self.bodies.fill(None)
        self.count = 0

    def reset_forces(self) -> None:
        for i in range(self.count):
            self.bodies[i].reset_force()

    def update(self) -> None:
        for i in range(self.count):
            self.bodies[i].update()

    def __iter__(self):
        for i in range(self.count):
            yield self.bodies[i]
    
    def __len__(self) -> int:
        return self.count
    
    def __contains__(self, item: Body) -> bool:
        return any(self.bodies[i] == item for i in range(self.count))
    
    def index(self, item: Body) -> int:
        for i in range(self.count):
            if self.bodies[i] == item:
                return i
        raise ValueError(f"Body {item} not found in BodyList.")
    
    def __str__(self) -> str:
        return f"BodyList(num_bodies={self.count})"
    
    def __repr__(self) -> str:
        return f"BodyList.from_bodies({self.bodies[:self.count]})"
