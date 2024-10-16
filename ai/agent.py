from bh import BarnesHut


class Agent:
    """
    Abstract base class for AI agents. They move around autonomously and interact
    with the Space Sandbox environment.

    This abstract class provides no implementation, but it does define the interface
    that all agents must implement.
    """

    def __init__(self):
        pass

    def act(self):
        """
        Perform an action in the environment.

        Normally, we apply forces to the agent (which may be a composite
        body) to make it dynamically respond to the environment.

        Forces will also be acting on the agent from the environment, so
        the agent must be able to sense the environment and update its
        state accordingly.
        """
        raise NotImplementedError

    def update(self):
        """
        Update the agent's state. This accepts no arguments because the agent
        should be able to update itself based on its internal state, and the
        environment (e.g., massive bodies gravitationally attracting the agent)
        will act on the agent to change its state as well.
        """
        raise NotImplementedError
    
    def sense(self):
        """
        Sense the environment.

        This method should return a list of objects in the environment that
        the agent can sense. The agent can then use this information to make
        decisions about how to act. It will this update its state in some way.
        """
        raise NotImplementedError
    

class SubsumptionAgent(Agent):
    """
    An agent that uses the subsumption architecture to make decisions.
    """    

    def __init__(self):
        super().__init__()

        self.behaviors = []
        self.active_behavior = None
        self.behavior_map = {}
        self.sensors = []
        
    def act(self):
        """

        """

    def update(self):
        pass

    def sense(self):
        pass


class ProximitySensor:
    def __init__(self, agent, range):
        self.agent = agent
        self.range = range

    def get_data(self):
        # Detect objects within a certain range of the agent
