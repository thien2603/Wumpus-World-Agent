# constants.py
N = 8          # kích thước bản đồ (override in main if needed)
K = 2
PIT_PROB = 0.1

DIRECTIONS = ['N', 'E', 'S', 'W']
DX = {'N': 0, 'E': 1, 'S': 0, 'W': -1}
DY = {'N': 1, 'E': 0, 'S': -1, 'W': 0}

BASE_CELL_SIZE = 60
MIN_CELL_SIZE = 20
MAX_CELL_SIZE = 120

WINDOW_WIDTH = N * BASE_CELL_SIZE
WINDOW_HEIGHT = N * BASE_CELL_SIZE

# Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)
BLUE = (0, 100, 255)
OLIVE = (128, 128, 0)

