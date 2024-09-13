import numpy as np
import random
import pickle
from game_action import GameAction
from players.player import Player

class QLearningAgent(Player):
    def __init__(self, number_of_dots=4, epsilon=0.05, alpha=0.01, gamma=0.9, load_q_table=False, q_table_file="q_table.pkl"):
        super().__init__()
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.q_table = {}  # Q-value table
        self.number_of_dots = number_of_dots
        self.last_state = None
        self.last_action = None
        self.last_reward = 0
        self.player_name = "QLearningAgent"
        self.q_table_file = q_table_file

        if load_q_table:
            self.load_q_table()

    def get_state(self, board_status, row_status, col_status):
        # Flatten and tuple the board status for a simplified state representation
        return (tuple(board_status.flatten()), tuple(row_status.flatten()), tuple(col_status.flatten()))

    def choose_action(self, state, available_actions):
        # Choose action based on epsilon-greedy policy
        if np.random.rand() < self.epsilon:
            return random.choice(available_actions)
        else:
            q_values = np.array([self.q_table.get((state, action), 0) for action in available_actions])
            max_q = np.max(q_values)
            best_actions = [action for action, q_value in zip(available_actions, q_values) if q_value == max_q]
            return random.choice(best_actions)

    def update_q_table(self, state, action, reward, next_state, next_available_actions):
        old_value = self.q_table.get((state, action), 0)
        future_q = max([self.q_table.get((next_state, a), 0) for a in next_available_actions], default=0)
        new_value = old_value + self.alpha * (reward + self.gamma * future_q - old_value)
        self.q_table[(state, action)] = new_value

    def get_action(self, game_state) -> GameAction:
        current_state = self.get_state(game_state.board_status, game_state.row_status, game_state.col_status)
        available_actions = self.get_available_actions(game_state)

        if self.last_state is not None:
            self.update_q_table(self.last_state, self.last_action, self.last_reward, current_state, available_actions)

        action = self.choose_action(current_state, available_actions)

        self.last_state = current_state
        self.last_action = action

        return GameAction(action[0], action[1])

    def reward(self, points_scored):
        self.last_reward = 1 if points_scored else -0.1

    def end_game(self, result):
        if result == 'win':
            self.last_reward = 1
        elif result == 'loss':
            self.last_reward = -1
        else:
            self.last_reward = 0

        self.update_q_table(self.last_state, self.last_action, self.last_reward, None, [])
        self.save_q_table()  # Save the Q-table after each game
        self.last_state = None
        self.last_action = None
        self.last_reward = 0

    def get_available_actions(self, game_state):
        available_actions = []
        for y in range(self.number_of_dots):
            for x in range(self.number_of_dots - 1):
                if game_state.row_status[y][x] == 0:
                    available_actions.append(('row', (x, y)))
        for y in range(self.number_of_dots - 1):
            for x in range(self.number_of_dots):
                if game_state.col_status[y][x] == 0:
                    available_actions.append(('col', (x, y)))
        return available_actions

    def is_clickable(self):
        return False

    def get_player_name(self) -> str:
        return self.player_name

    def save_q_table(self):
        try:
            with open(self.q_table_file, 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"Q-table saved to {self.q_table_file}")
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def load_q_table(self):
        try:
            with open(self.q_table_file, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Q-table loaded from {self.q_table_file}")
        except FileNotFoundError:
            print("No existing Q-table found. Starting with a fresh Q-table.")
        except Exception as e:
            print(f"Error loading Q-table: {e}")
