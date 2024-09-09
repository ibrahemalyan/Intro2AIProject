from abc import ABC, abstractmethod
from game_action import GameAction


class Player(ABC):

    @abstractmethod
    def get_action(self, state) -> GameAction:
        pass

    def is_clickable(self) -> bool:
        return False

    @abstractmethod
    def get_player_name(self) -> str:
        pass
