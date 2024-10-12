from pygame.math import Vector2 as vec2
from model.body import Body
from typing import List, Tuple, Callable, Optional
from model.body_list import BodyList

class Node:
    """
    Represents a node in the quadtree/octree.
    
    Attributes:
    -----------
    center : vec2
        The spatial center of this node.
    width : float
        The width of the region represented by this node.
    mass : float
        The total mass of the bodies contained within this region.
    mass_center : vec2
        The center of mass of the bodies within this region.
    body : Any
        The body contained in this node (if it's a leaf node).
    children : list
        The sub-regions (if it's an internal node).
    """
    def __init__(self, center : vec2, width : float):
        self.center = center
        self.width = width
        self.mass = 0.0
        self.mass_center = vec2(0, 0)
        self.body = None
        self.children = []

    def is_leaf(self):
        """Check if the node is a leaf (i.e., contains a body but no sub-regions)."""
        return len(self.children) == 0
    
    @property
    def pos(self):
        return self.mass_center
    
    @property
    def density(self):
        return self.mass / self.area
    
    @property
    def area(self):
        return self.width ** 2
        
class BarnesHut:
    """
    Barnes-Hut algorithm for efficient N-body simulation.
    
    This class is designed for general-purpose force calculations, such as gravitational,
    electrostatic, or thermal forces.
    
    Attributes:
    -----------
    theta : float
        Threshold for Barnes-Hut approximation; determines when to treat a group of bodies
        as a single pseudo-body (center of mass approximation).

    Methods:
    --------
    insert_body(node, body):
        Inserts a body into the quadtree.
    calculate_force(body, node, force_model):
        Recursively calculates forces on a body due to a node (or its center of mass if internal).
    build_tree(bodies, region_center, region_width):
        Builds the quadtree for a given set of bodies.
    compute_forces(bodies, force_model, region_center, region_width):
        Computes forces on each body in the system using the provided force model.
    """

    def __init__(self, theta : float = 0.5):
        """
        Parameters:
        -----------
        theta : float, optional
            The threshold for Barnes-Hut approximation (default is 0.5).
            If theta is small, more accurate but slower. If larger, faster but less accurate.
        """
        self.theta = theta
        self.root = None
        self.overlapping_pairs : List[Tuple[Body, Body]] = []

    def _insert_body(self, node: Node, body: Body) -> None:
        if node.body is None and node.is_leaf():
            node.body = body
            node.mass = body.mass
            node.mass_center = body.pos
        else:
            if node.is_leaf():
                self._subdivide(node)
                self._insert_body(node, node.body)
                node.body = None  # Clear the body since it's now internal
            
            for child in node.children:
                if self._contains(child, body):
                    self._insert_body(child, body)
                    break
            
            node.mass = sum(child.mass for child in node.children)            
            if node.mass > 0:
                node.mass_center = sum(
                    (child.mass * child.mass_center for child in node.children), vec2(0, 0)
                ) / node.mass
            else:
                node.mass_center = vec2(0, 0)

    def _contains(self, node : Node, body : Body) -> bool:
        """
        Checks if a body is within the region of a node.

        Parameters:
        -----------
        node : Node
            The node representing a region in space.
        body : Body
            A body object.
        
        Returns:
        --------
        bool
            True if the body is within the bounds of the node's region, False otherwise.
        """
        half_width = node.width / 2
        return (
            node.center.x - half_width <= body.pos.x < node.center.x + half_width and
            node.center.y - half_width <= body.pos.y < node.center.y + half_width
        )

    def _subdivide(self, node : Node) -> None:
        """
        Subdivide a node into four child nodes, splitting the region.

        Parameters:
        -----------
        node : Node
            The node to subdivide into four children.
        """
        half_width = node.width / 2
        quarter_width = node.width / 4
        for dx in [-quarter_width, quarter_width]:
            for dy in [-quarter_width, quarter_width]:
                child_center = node.center + vec2(dx, dy)
                child_node = Node(child_center, half_width)
                node.children.append(child_node)

    def _calculate_force(self, body: Body, node: Node, force_model) -> vec2:
        """
        Recursively calculate the force on a body due to a node or the center of mass of a node.
        
        Parameters:
        -----------
        body : Body
            A body object.
        node : Node
            A node in the quadtree that may represent an aggregated group of bodies.
        force_model : function
            A user-defined force model function that takes a pair of bodies and
            returns a force vector.

        Returns:
        --------
        vec2
            The total force acting on the body
        """
        if node.is_leaf() and node.body is body:
            return vec2(0, 0)
        
        d = (node.mass_center - body.pos).length()
        # Use center of mass approximation if node is far enough
        if node.is_leaf() or node.width / d < self.theta:
            return force_model(body, node)

        # Otherwise, sum the forces from the children
        total_force = vec2(0, 0)
        for child in node.children:
            total_force += self._calculate_force(body, child, force_model)
        return total_force

    def build_tree(self,
                   bodies: BodyList,
                   region_center: Optional[vec2] = None,
                   region_width: Optional[float] = None):
        """
        Build the quadtree for a set of bodies in a given region.

        Parameters:
        -----------
        bodies : BodyList
            A list of body objects
        region_center : vec2
            The center of the root region (usually the center of all bodies).
        region_width : float
            The width of the root region (should encompass all bodies).

        Returns:
        --------
        Node
            The root node of the constructed quadtree.
        """
        self.clear()
        if len(bodies) == 0:
            return
            
        if region_center is None:
            region_center = vec2(0, 0)
            for body in bodies:
                region_center += body.pos
            region_center /= len(bodies)

        if region_width is None:
            max_distance = max((body.pos - region_center).length() for body in bodies)
            region_width = 2 * max_distance

        self.root = Node(region_center, region_width)
        for body in bodies:
            self._insert_body(self.root, body)


    def query(self, pos: vec2) -> Optional[Node]:
        """
        Query the quadtree to find the leaf node containing a given position.

        Parameters:
        -----------
        pos : vec2
            A 2D position vector.

        Returns:
        --------
        Node
            The leaf node containing the position, or None if no such node exists.
        """
        if self.root is None:
            raise ValueError("Quadtree has not been built yet. Call build_tree() first.")
        
        return self._query(self.root, pos)
    
    def _query(self, node: Node, pos: vec2) -> Optional[Node]:
        if node.is_leaf():
            return node
        
        for child in node.children:
            if self._contains(child, pos):
                return self._query(child, pos)
        return None

    def clear(self):
        """Clear the quadtree."""
        self.root = None
        self.overlapping_pairs = []

    def compute_forces(self,
                       bodies : BodyList,
                       force_model : Callable[[Body, Body], vec2]) -> None:
        """
        Compute forces on each body using the Barnes-Hut approximation.

        Parameters:
        -----------
        bodies : list
            A list of body objects, each with at least a `position` and `mass` attribute.
        force_model : function
            A user-defined force model function that calculates the pairwise force between bodies.
        """
        #if self.root is None:
        #    raise ValueError("Quadtree has not been built yet. Call build_tree() first.")
        
        for i in range(len(bodies)):
            body = bodies[i]
            force = self._calculate_force(body, self.root, force_model)
            body.force += force

    def _bodies_overlap(self, body1: Body, body2: Body) -> bool:
        delta_pos = body1.pos - body2.pos
        dist_val = delta_pos.length()
        min_dist = body1.radius + body2.radius
        return dist_val < min_dist

    def _regions_overlap(self, body: Body, node: Node) -> bool:
        half_width = node.width / 2
        dx = abs(body.pos.x - node.center.x)
        dy = abs(body.pos.y - node.center.y)
        return dx < (body.radius + half_width) and dy < (body.radius + half_width)

    def _check_overlap(self, node: Node, root: Node, checked: set) -> None:
        if root.is_leaf():
            if root.body is not None and root.body is not node.body:
                if self._bodies_overlap(node.body, root.body):
                    # Create a unique identifier for the pair to avoid duplicates
                    pair_ids = tuple(sorted((id(node.body), id(root.body))))
                    if pair_ids not in checked:
                        self.overlapping_pairs.append((node.body, root.body))
                        checked.add(pair_ids)
        else:
            for child in root.children:
                if self._regions_overlap(node.body, child):
                    self._check_overlap(node, child, checked)

    def compute_overlapping_pairs(self) -> None:
        """
        Compute all overlapping pairs of bodies in the quadtree.
        """
        #if self.root is None:
        #    raise ValueError("Quadtree has not been built yet. Call build_tree() first.")
        
        checked = set()
        self._compute_overlapping_pairs(self.root, checked)

    def _compute_overlapping_pairs(self, node: Node, checked: set) -> None:
        if node.is_leaf():
            if node.body is not None:
                self._check_overlap(node, self.root, checked)
        else:
            for child in node.children:
                self._compute_overlapping_pairs(child, checked)

    def compute_local_forces(self,
                             force_model: Callable[[Body, Body], vec2]) -> None:
        """
        Compute local forces between relevant body pairs using a provided force model.
        
        Parameters:
        -----------
        bodies : BodyList
            A list of body objects.
        force_model : function
            A user-defined local force model function that calculates the force between two bodies.
            It should have the signature: force_model(body1: Body, body2: Body) -> vec2
        """
        #if self.root is None:
        #    raise ValueError("Quadtree has not been built yet. Call build_tree() first.")

        # Compute local forces for each overlapping pair in the body list
        for body1, body2 in self.overlapping_pairs:
            force = force_model(body1, body2)
            body1.force += force
            body2.force -= force  # Apply Newton's third law