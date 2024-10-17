from model.body import Body
import numpy as np

class BodyList:
    def __init__(self, max_bodies: int):
        self.bodies : np.array = np.empty(0, dtype=Body)

    def __getitem__(self, index: int) -> Body:
        return self.bodies[index]
    
    def __setitem__(self, index: int, value: Body) -> None:
        self.bodies[index] = value

    def add(self, value: Body) -> None:
        self.bodies = np.append(self.bodies, value)
        

    def remove(self, index) -> None:
        self.bodies = np.delete(self.bodies, index)

    @property
    def num_bodies(self) -> int:
        return len(self.bodies)

    def remove_item(self, item: Body) -> None:
        self.bodies = np.delete(self.bodies, np.where(self.bodies == item))

    def clear(self) -> None:
        self.bodies = np.empty(0, dtype=Body)

    def __iter__(self):
        return iter(self.bodies)
    
    def __len__(self) -> int:
        return len(self.bodies)
    
    def __contains__(self, item: Body) -> bool:
        return item in self.bodies
    
    def index(self, item: Body) -> int:
        return np.where(self.bodies == item)[0][0]
    
    def __str__(self) -> str:
        return f"BodyList(num_bodies={len(self.bodies)})"