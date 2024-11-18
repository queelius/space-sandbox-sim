import pygame

class SimState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimState, cls).__new__(cls)
            cls._instance.current_time_ms = 0
            cls._instance.last_time_ms = 0
            cls._instance.paused = False
            cls._instance.delta = None
        return cls._instance
    
    def pause(self):
        """
        Pause the simulation.
        """
        if not self.paused:
            self.paused = True
            self.delta = self.current_time_ms - self.last_time_ms

    def resume(self):
        """
        Resume the simulation. When we resume the simulation, the current time
        will be the time when we resumed.
        """
        if self.paused:
            self.paused = False        
            self.current_time_ms = pygame.time.get_ticks()
            self.last_time_ms = self.current_time_ms - self.delta

    def update(self, time_ms: int) -> None:
        """
        Update the state with the current time in milliseconds.

        Parameters:
        ----------
        time_ms : int
            The current time in milliseconds.

        """
        if self.paused:
            return
        self.last_time_ms = self.current_time_ms
        self.current_time_ms = time_ms

    @property
    def time_step_ms(self) -> int:
        """
        Get the time step in milliseconds.
        """
        return self.current_time_ms - self.last_time_ms
    
    @property
    def time_step(self) -> float:
        """
        Get the time step in seconds
        """
        return self.time_step_ms / 1000.0
    
    @property
    def elapsed_time(self) -> float:
        """
        Get the elapsed time the simulation has been running in seconds.
        """
        return self.current_time_ms / 1000.0
    

        
    