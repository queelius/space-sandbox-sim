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

# 1 DT = 100 hours, so we scale all physical constants to make the simulation
# work accurately with the chosen units
DT = 1.0 / FPS  # Time step

# m^3 kg^-1 s^-2
REAL_GRAVITY = 6.67430e-11
GRAVITY = REAL_GRAVITY * 1e8  # Gravitational constant

REAL_LIGHT_SPEED = 299792458  # m/s
LIGHT_SPEED = math.sqrt(REAL_LIGHT_SPEED) * 1e-3  # Speed of light

REPULSION_STRENGTH = 25.0 # Strength of the repulsive force for collisions
DAMPING = 150.0
MERGE_RATIO = 0.7

MAX_BODIES : int = 10000