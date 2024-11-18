from typing import Callable
from model.body import Body

class Condition:
    """
    Encapsulates a condition function between two `Body` instances and allows
    for logical composition using the & (AND), | (OR), and ~ (NOT) operators.

    The condition functions are callable objects that take two `Body` instances
    and return a boolean indicating whether the condition is satisfied.

    This class enables intuitive composition of conditions, making it easier to
    build complex conditions from simpler ones, applicable to various contexts
    like merging bodies, creating springs, etc.
    """

    def __init__(self, func: Callable[[Body, Body], bool]) -> None:
        """
        Initializes the Condition object with a given function.

        Args:
            func (Callable[[Body, Body], bool]): A function that takes two `Body`
            instances and returns a boolean indicating if the condition is met.
        """
        self.func: Callable[[Body, Body], bool] = func

    def __call__(self, body1: Body, body2: Body) -> bool:
        """
        Evaluates the condition function with the given bodies.

        Args:
            body1 (Body): The first body.
            body2 (Body): The second body.

        Returns:
            bool: The result of the condition function.
        """
        return self.func(body1, body2)

    def __and__(self, other: 'Condition') -> 'Condition':
        """
        Returns a new Condition that is the logical AND of this condition and another.

        Args:
            other (Condition): Another condition to combine with.

        Returns:
            Condition: A new Condition representing the logical AND of both conditions.
        """
        return Condition(lambda b1, b2: self(b1, b2) and other(b1, b2))

    def __or__(self, other: 'Condition') -> 'Condition':
        """
        Returns a new Condition that is the logical OR of this condition and another.

        Args:
            other (Condition): Another condition to combine with.

        Returns:
            Condition: A new Condition representing the logical OR of both conditions.
        """
        return Condition(lambda b1, b2: self(b1, b2) or other(b1, b2))

    def __invert__(self) -> 'Condition':
        """
        Returns a new Condition that is the logical NOT of this condition.

        Returns:
            Condition: A new Condition representing the logical NOT of this condition.
        """
        return Condition(lambda b1, b2: not self(b1, b2))
