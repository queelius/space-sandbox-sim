import math

WIDTH, HEIGHT = 2400, 1200
BACKGROUND_COLOR = (0, 0, 20)
FPS = 60

# Colors for celestial objects
COLORS = [
    (255, 255, 255),   # White
    (255, 215, 0),     # Gold
    (173, 216, 230),   # Light Blue
    (255, 69, 0),      # Red-Orange
    (255, 0, 0),       # Red
    (0, 255, 0),       # Green
    (0, 0, 255),       # Blue
    (255, 0, 255),     # Magenta
    (0, 255, 255),     # Cyan
    (255, 255, 0),     # Yellow
    (255, 140, 0),     # Orange
    (128, 0, 128),     # Purple
    (128, 0, 0),       # Maroon
    (0, 128, 0),       # Green
    (0, 0, 128),       # Navy
    (0, 128, 128),     # Teal
    (128, 128, 0),     # Olive
    (128, 128, 128),   # Gray
    (192, 192, 192),   # Silver
    ( 0,   0,   0),   # Black
]

HIGHLIGHT_COLOR = (192, 192, 192)  # Silver for highlighting selected body

NEWTON_UNIV_GRAVITY = 6.67430e-11 # m^3 kg^-1 s^-2
SIM_GRAVITY = NEWTON_UNIV_GRAVITY * 1e7

LIGHT_SPEED = 299792458  # 2.99792458e8 m/s
SIM_LIGHT_SPEED = math.sqrt(LIGHT_SPEED) # 1.7315e4 m/s

REPULSION_STRENGTH = 200.0 # Strength of the repulsive force for collisions
REPULSION_DAMPING = 10.0

MERGE_RATIO = 0.7

MAX_BODIES : int = 10000
SPRING_STIFFNESS = 10
SPRING_DAMPING = 1
SPRING_BREAK_FORCE = float('inf')
SPRING_BREAK_DISTANCE_FACTOR = 3
NEIGHBORHOOD_RADIUS = 5