from game_action import GameAction
from Renderers.gui_renderer import GUI_Renderer
from players.player import Player


class HumanPlayer(Player):
    def __init__(self, renderer:GUI_Renderer):
        self.renderer = renderer
        self.name = "Human Player"

    def get_action(self, event) -> GameAction:
        grid_position = [event.x, event.y]
        return GameAction(*self.renderer.convert_grid_to_logical_position(grid_position))

    def is_clickable(self) -> bool:
        return True

    def get_player_name(self) -> str:
        return self.name

