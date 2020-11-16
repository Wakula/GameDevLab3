import enum

class Directions(enum.Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'


DIRECTIONS_TO_DELTA = {
    Directions.LEFT: (-1, 0),
    Directions.UP: (0, -1),
    Directions.RIGHT: (1, 0),
    Directions.DOWN: (0, 1)
}