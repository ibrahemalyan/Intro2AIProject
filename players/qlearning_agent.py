import random
import pickle
import os
from players.player import Player
from game_state import GameState

class QLearningAgent(Player):


    def __init__(self,filename='QLstate.pickle', discount_factor=0.5, learning_rate=0.8, epsilon=0.2,load_q_table=False):
        self.q_table = {}
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.q_table_file = filename

        self.last_state = None
        self.last_action = None
        self.training = True

        if load_q_table:
            self.load_q_table()

    def get_state_key(self, state: GameState):
        """Convert the GameState into a tuple (hashable) to use as a key for Q-table."""
        return (tuple(state.board_status.flatten()),
                tuple(state.row_status.flatten()),
                tuple(state.col_status.flatten()),
                state.player1_turn)

    def get_action(self, state):
        """Choose an action based on epsilon-greedy strategy."""
        actions = state.get_valid_moves()
        self.last_state = state
        state_key = self.get_state_key(state)


        max_q_value = -float('inf')
        self.last_action = -1

        # Exploration vs. Exploitation (Epsilon-Greedy Strategy)
        choice = random.random()
        eps_threshold = 1 - self.epsilon - (self.epsilon / len(actions))

        # Explore
        if choice > eps_threshold:
            # Randomly pick an action
            self.last_action = random.choice(list(actions))
            # print(f"Exploring: chose action {self.last_action} for state {state}")
        # Exploit
        else:
            if state_key not in self.q_table:
                self.q_table[state_key] = {action: -1 for action in state.get_valid_moves()}

            # Choose the action with the highest Q-value
            self.last_action = max(self.q_table[state_key], key=self.q_table[state_key].get)
        return self.last_action

    def reward(self, feedback, new_state, actions):
        """Update the Q-value using the Q-learning update rule."""
        q_prev = self.q_table[self.last_state][self.last_action]

        max_q_new_state = 0
        if actions:
            max_q_new_state = max(self.q_table[new_state][action] for action in actions)

        # Q-learning formula: Q(s, a) = Q(s, a) + lr * (reward + discount * max(Q(s', a')) - Q(s, a))
        q_new = q_prev + self.learning_rate * (feedback + self.discount_factor * max_q_new_state - q_prev)

        # Save updated Q-value
        self.update_q_value(self.last_state, self.last_action, q_new)


    def update_q_value(self, state, action, q_new):
        """Update the Q-value based on the reward and the new state."""
        state_key = self.get_state_key(state)
        self.q_table[state_key][action] = q_new

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

