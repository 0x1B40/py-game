"""
Configuration constants for RL Space Adventure game.
"""

# Game dimensions
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Game limits
MAX_COINS = 3
MAX_ENEMIES = 2

# Colors (RGB tuples)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)

# Q-Learning parameters
ALPHA = 0.1  # Learning rate
GAMMA = 0.95  # Discount factor
EPSILON_START = 0.2  # Initial exploration rate
EPSILON_END = 0.01  # Minimum exploration rate
EPSILON_DECAY = 0.995  # Exploration decay rate

# State discretization
STATE_BINS = 4
FUEL_BINS = 4

# Actions: (dx, dy) - stay, up, down, left, right
ACTIONS = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]

# Rewards
FUEL_CONSUMPTION_REWARD = -0.1
COIN_COLLECTION_REWARD = 20
ENEMY_COLLISION_REWARD = -50
FUEL_DEPLETION_REWARD = -100
FUEL_RESTORE_PER_COIN = 5
