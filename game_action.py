from typing import Literal, Tuple

class GameAction:
    """
    action_type: "row" or "col" draws a horizontal or vertical line
    position: (x: int, y: int) position in grid, starting from (0, 0)
    """
    def __init__(self, action_type: Literal["row", "col"], position: Tuple[int, int]):
        self.action_type = action_type
        self.position = position
