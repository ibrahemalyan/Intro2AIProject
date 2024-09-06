import numpy as np
import random
from game_action import GameAction
from game_state import GameState
from players.player import Player
from typing import Tuple


class QLearningAgent(Player):
    def __init__(self, epsilon=0.1, alpha=0.5, gamma=0.9):
        super().__init__()
        self.q_table = {}  # This will store the Q-values
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.last_state = None
        self.last_action = None
        self.last_reward = 0

    def get_q_value(self, state: Tuple) -> np.ndarray:
        """
        Retrieve the Q-values for all actions in a given state.
        If the state does not exist, it initializes it with 0 values.
        """
        if state not in self.q_table:
            self.q_table[state] = np.zeros(2)  # Assuming two possible actions (row or col)
        return self.q_table[state]

    def update_q_value(self, state: Tuple, action_index: int, reward: float, next_state: Tuple):
        """
        Updates the Q-value using the Q-learning update rule.
        """
        current_q = self.get_q_value(state)[action_index]
        future_q = max(self.get_q_value(next_state))  # Maximum Q-value of next state
        new_q_value = current_q + self.alpha * (reward + self.gamma * future_q - current_q)
        self.q_table[state][action_index] = new_q_value

    def choose_action(self, state) -> GameAction:
        """
        Chooses an action based on the epsilon-greedy strategy.
        """
        possible_actions = self.get_possible_actions(state)
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random action
            action_type, position = random.choice(possible_actions)
        else:
            # Exploitation: choose the best action based on Q-values
            action_type, position = self.get_best_action(state, possible_actions)
        return GameAction(action_type, position)

    def get_best_action(self, state, possible_actions):
        """
        Returns the action with the highest Q-value from the possible actions.
        """
        best_action = None
        best_value = -float('inf')

        for action_type, position in possible_actions:
            action_index = 0 if action_type == 'row' else 1
            q_value = self.get_q_value(state)[action_index]

            if q_value > best_value:
                best_value = q_value
                best_action = (action_type, position)

        return best_action

    def get_possible_actions(self, state):
        """
        Return a list of possible actions given the current game state.
        """
        possible_actions = []

        # Check for available rows and columns (not yet marked)
        for y in range(len(state.row_status)):
            for x in range(len(state.row_status[0])):
                if state.row_status[y][x] == 0:  # Available row
                    possible_actions.append(('row', (x, y)))

        for y in range(len(state.col_status)):
            for x in range(len(state.col_status[0])):
                if state.col_status[y][x] == 0:  # Available col
                    possible_actions.append(('col', (x, y)))

        return possible_actions

    def get_action(self, state: GameState) -> GameAction:
        action = self.choose_action(state)
        # Save last state and action for updating Q-table after receiving a reward
        self.last_state = state
        self.last_action = action
        return action

    def update_q_table_after_turn(self, reward: float, new_state):
        """
        After the environment responds with a reward and a new state,
        update the Q-table for the previous action.
        """
        new_state_key = (tuple(map(tuple, new_state.row_status)), tuple(map(tuple, new_state.col_status)))

        action_index = 0 if self.last_action.action_type == 'row' else 1
        self.update_q_value(self.last_state, action_index, reward, new_state_key)

    def get_player_name(self) -> str:
        return "QLearningAgent"
