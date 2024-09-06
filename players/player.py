from abc import ABC, abstractmethod
from game_action import GameAction
import time

class Player(ABC):

    def __init__(self):
        self.steps = 0  # Track the number of steps (actions)
        self.start_time = None  # Track the start time of the game
        self.end_time = None  # Track the end time of the game

    @abstractmethod
    def get_action(self, state) -> GameAction:
        pass

    def increment_steps(self):
        """Increments the step counter for the player."""
        self.steps += 1

    def is_clickable(self) -> bool:
        """Defines if the player is clickable (for human players). Default is False."""
        return False

    def start_timer(self):
        """Starts the timer for tracking game duration."""
        self.start_time = time.time()

    def end_timer(self):
        """Ends the timer and captures the time when the game finishes."""
        self.end_time = time.time()

    def get_total_time(self):
        """Calculates the total time taken by the player."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @abstractmethod
    def get_player_name(self) -> str:
        pass
