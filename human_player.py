from game_action import GameAction
from game_renderer import GameRenderer
from player import Player


class HumanPlayer(Player):
    def __init__(self, renderer:GameRenderer):
        self.renderer = renderer
        self.name = "Human Player"

    def get_action(self, event) -> GameAction:
        grid_position = [event.x, event.y]
        return GameAction(*self.renderer.convert_grid_to_logical_position(grid_position))

    def is_clickable(self) -> bool:
        return True

    def get_player_name(self) -> str:
        return self.name

