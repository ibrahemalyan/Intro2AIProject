import numpy as np
from game_state import GameState
from game_action import GameAction
from players.player import Player
import random

class QLearningAgent(Player):
    def __init__(self, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995):
        self.q_table = {}  # {(state, action): q_value}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.name = "QLearning Agent"

    def get_player_name(self):
        return self.name

    def get_action(self, state: GameState) -> GameAction:
        state_tuple = self.state_to_tuple(state)
        if random.uniform(0, 1) < self.exploration_rate:
            action = self.get_random_action(state)
        else:
            action = self.get_best_action(state_tuple)
        return action

    def update_q_value(self, prev_state, action, reward, next_state):
        prev_state_tuple = self.state_to_tuple(prev_state)
        next_state_tuple = self.state_to_tuple(next_state)
        prev_q_value = self.q_table.get((prev_state_tuple, action), 0)
        best_future_q = max([self.q_table.get((next_state_tuple, a), 0) for a in self.get_all_possible_actions(next_state)], default=0)
        new_q_value = prev_q_value + self.learning_rate * (reward + self.discount_factor * best_future_q - prev_q_value)
        self.q_table[(prev_state_tuple, action)] = new_q_value

    def get_best_action(self, state_tuple):
        possible_actions = self.get_all_possible_actions(state_tuple)
        best_action = max(possible_actions, key=lambda action: self.q_table.get((state_tuple, action), 0))
        return best_action

    def get_random_action(self, state: GameState) -> GameAction:
        action_type = random.choice(["row", "col"])
        if action_type == "row":
            position = self.get_random_position_with_zero_value(state.row_status)
        else:
            position = self.get_random_position_with_zero_value(state.col_status)
        return GameAction(action_type, position)

    def get_random_position_with_zero_value(self, matrix: np.ndarray):
        [ny, nx] = matrix.shape
        x = -1
        y = -1
        valid = False
        while not valid:
            x = random.randrange(0, nx)
            y = random.randrange(0, ny)
            valid = matrix[y, x] == 0
        return (x, y)

    def get_all_possible_actions(self, state: GameState):
        actions = []
        for y, row in enumerate(state.row_status):
            for x, val in enumerate(row):
                if val == 0:
                    actions.append(GameAction("row", (x, y)))
        for y, col in enumerate(state.col_status):
            for x, val in enumerate(col):
                if val == 0:
                    actions.append(GameAction("col", (x, y)))
        return actions

    def state_to_tuple(self, state: GameState):
        return (tuple(state.board_status.flatten()), tuple(state.row_status.flatten()), tuple(state.col_status.flatten()))

    def update_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay
