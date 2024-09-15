import os
import pickle

import numpy as np
import random
from game_action import GameAction
from players.player import Player
from game_state import GameState


class QLearningAgent(Player):
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1, load_q_table=False,
                 q_table_file=None):
        self.q_table = {}  # A dictionary to store Q-values
        self.learning_rate = learning_rate
        self.q_table_file = q_table_file
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.last_state_action = None  # Track the last state-action pair
        if load_q_table:
            self.load_q_table()

    def get_state_key(self, state: GameState):
        """Convert the GameState into a tuple (hashable) to use as a key for Q-table."""
        return (tuple(state.board_status.flatten()),
                tuple(state.row_status.flatten()),
                tuple(state.col_status.flatten()),
                state.player1_turn)

    def get_action(self, state: GameState) -> GameAction:
        """Decide the next action using an epsilon-greedy policy."""
        state_key = self.get_state_key(state)

        if random.random() < self.epsilon:
            # Exploration: random move
            valid_moves = state.get_valid_moves()
            return random.choice(valid_moves)
        else:
            # Exploitation: choose the best move from Q-table
            if state_key not in self.q_table:
                self.q_table[state_key] = {action: 0.0 for action in state.get_valid_moves()}

            best_action = max(self.q_table[state_key], key=self.q_table[state_key].get)
            self.last_state_action = (state, best_action)
            self.reward(self.turn_end_reward(state,state.generate_successor(best_action)))
            return best_action

    def update_q_value(self, old_state, action, reward, new_state):
        """Update the Q-value based on the reward and the new state."""
        old_state_key = self.get_state_key(old_state)
        new_state_key = self.get_state_key(new_state)

        if old_state_key not in self.q_table:
            self.q_table[old_state_key] = {action: 0.0 for action in old_state.get_valid_moves()}
        if new_state_key not in self.q_table:
            self.q_table[new_state_key] = {action: 0.0 for action in new_state.get_valid_moves()}

        old_q_value = self.q_table[old_state_key][action]
        max_future_q_value = max(self.q_table[new_state_key].values())

        # Q-learning formula
        new_q_value = old_q_value + self.learning_rate * (
                reward + self.discount_factor * max_future_q_value - old_q_value)
        self.q_table[old_state_key][action] = new_q_value

    def reward(self, feedback):
        """At the end of the game, adjust rewards based on win/loss."""

        # Update the last state-action pair with the final result
        if self.last_state_action is not None:
            last_state, last_action = self.last_state_action
            self.update_q_value(last_state, last_action, feedback, last_state)

    def save_q_table(self):
        """Save the Q-table to a file."""
        with open(self.q_table_file, 'wb') as file:
            pickle.dump(self.q_table, file)
        print(f"Q-table saved to {self.q_table_file}")

    def load_q_table(self):
        """Load the Q-table from a file if it exists."""
        if os.path.exists(self.q_table_file):
            with open(self.q_table_file, 'rb') as file:
                self.q_table = pickle.load(file)
            print(f"Q-table loaded from {self.q_table_file}")
        else:
            print(f"No Q-table file found. Starting fresh.")

    def get_player_name(self):
        return "QLearningAgent"

    @staticmethod
    def turn_end_reward(state_before: GameState, state_after: GameState):
        """
        Reward function based on the number of boxes completed in the turn.
        Returns +1 for each box completed.
        """
        # Count the number of boxes completed before and after the move
        boxes_before = np.sum(np.abs(state_before.board_status) == 4)
        boxes_after = np.sum(np.abs(state_after.board_status) == 4)

        # Reward for each new box completed
        reward = boxes_after - boxes_before
        return reward if reward > 0 else 0

    @staticmethod
    def round_end_reward(result):
        """
        Reward function based on whether the agent won the round.
        Returns +10 for a win and -10 for a loss.
        """
        if result == 'win':
            return 10
        elif result == 'loss':
            return -10
        return 0

