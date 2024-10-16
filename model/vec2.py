    
from pygame.math import Vector2

class pos(Vector2):
    """
    A custom position class that is optimized for Verlet integration.

    This class is a subclass of pygame.math.Vector2, and it overrides the
    
    """

    def __iadd__(self, value):
        """
        """
        print("In __iadd__")
        delta = self._pos - self._old_pos
        self._pos += value
        self._old_pos += value - delta

        return self
    
    def __isub__(self, value):
        """
        Since self.pos is a property, and when we modify the position, we
        must also modify the old position so that it is consistent with the
        velocity calculation. So, we override the -= in-place operator to
        do the necessary updates.
        """
        print("In __isub__")
        self.pos = self.pos - value
        return self
    
    def _unsupported_op(self, op_name):
        raise TypeError(f"In-place {op_name} operation is not supported for 'pos' attribute.")

    __imul__ = lambda self, other: self._unsupported_op('*=')
    __itruediv__ = lambda self, other: self._unsupported_op('/=')
    __imod__ = lambda self, other: self._unsupported_op('%=')
    __ipow__ = lambda self, other: self._unsupported_op('**=')    
    __ifloordiv__ = lambda self, other: self._unsupported_op('//=')
    __ilshift__ = lambda self, other: self._unsupported_op('<<=')
    __irshift__ = lambda self, other: self._unsupported_op('>>=')
    __iand__ = lambda self, other: self._unsupported_op('&=')
    __ixor__ = lambda self, other: self._unsupported_op('^=')
    __ior__ = lambda self, other: self._unsupported_op('|=')
    __neg__ = lambda self: self._unsupported_op('negation')
    __pos__ = lambda self: self._unsupported_op('positive')
    __abs__ = lambda self: self._unsupported_op('absolute')
    __invert__ = lambda self: self._unsupported_op('invert')
