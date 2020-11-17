import enum

class Directions(enum.Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'


DIRECTIONS_TO_DELTA = {
    Directions.LEFT: (-1, 0),
    Directions.UP: (0, -1),
    Directions.RIGHT: (1, 0),
    Directions.DOWN: (0, 1)
}