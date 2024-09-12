import math
import random

import numpy as np

from game_state import GameState
from players.player import Player
from game_action import GameAction
from typing import Tuple, Dict, List
from collections import defaultdict


class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # The game state
        self.parent = parent  # The parent node
        self.children = {}  # Map actions to child nodes
        self.visits = 0  # Number of times this node has been visited
        self.wins = 0  # Number of simulations this node has won

    def is_fully_expanded(self, possible_actions):
        return len(self.children) == len(possible_actions)

    def best_child(self, exploration_weight=1.414):
        """
        Return the child with the highest UCB1 score.
        """
        best_score = -float('inf')
        best_child = None
        for action, child in self.children.items():
            exploit = child.wins / child.visits if child.visits > 0 else 0
            explore = math.sqrt(math.log(self.visits) / child.visits) if child.visits > 0 else float('inf')
            ucb1_score = exploit + exploration_weight * explore
            if ucb1_score > best_score:
                best_score = ucb1_score
                best_child = (action, child)
        return best_child

    def expand(self, action, child_node):
        """
        Add a child node for the given action.
        """
        self.children[action] = child_node


class MCTSPlayer(Player):
    def __init__(self, simulations=10):
        super().__init__()
        self.simulations = simulations  # Number of MCTS simulations to run

    def get_action(self, state: GameState) -> GameAction:
        root = MCTSNode(state)  # Create the root node for MCTS

        for _ in range(self.simulations):
            node = self.selection(root)
            if not self.is_terminal(node.state):
                node = self.expansion(node)
            reward = self.simulation(node.state)
            self.backpropagation(node, reward)

        # Choose the child with the highest visit count as the best move
        best_action, _ = max(root.children.items(), key=lambda child: child[1].visits)
        return best_action

    def selection(self, node: MCTSNode) -> MCTSNode:
        """
        Traverse the tree to the most promising node using UCB1.
        """
        while not self.is_terminal(node.state) and node.is_fully_expanded(self.get_possible_actions(node.state)):
            action, node = node.best_child()
        return node

    def expansion(self, node: MCTSNode) -> MCTSNode:
        """
        Expand the node by adding one of the untried child states.
        """
        possible_actions = self.get_possible_actions(node.state)
        untried_actions = [action for action in possible_actions if action not in node.children]

        # Pick a random untried action
        action = random.choice(untried_actions)

        # Simulate the action and create a new game state
        new_state = self.simulate_action(node.state, action.action_type, action.position, node.state.player1_turn)
        child_node = MCTSNode(new_state, parent=node)
        node.expand(action, child_node)

        return child_node

    def simulation(self, state: GameState) -> float:
        """
        Simulate a random playout from the current state until the game ends.
        """
        current_state = state

        while not self.is_terminal(current_state):
            possible_actions = self.get_possible_actions(current_state)
            action = random.choice(possible_actions)  # Play random actions
            current_state = self.simulate_action(current_state, action.action_type, action.position,
                                                 current_state.player1_turn)

        # Return the final score (1 for player1 win, -1 for player2 win, 0 for tie)
        return self.evaluate_terminal_state(current_state)

    def backpropagation(self, node: MCTSNode, reward: float):
        """
        Propagate the result of the simulation back up the tree.
        """
        while node is not None:
            node.visits += 1
            node.wins += reward
            reward = -reward  # Alternate reward between players
            node = node.parent

    def simulate_action(self, state: GameState, action_type: str, position: Tuple[int, int],
                        player1_turn: bool) -> GameState:
        """
        Simulate taking an action in the current state. This function returns a new game state.
        """
        new_board_status = state.board_status.copy()
        new_row_status = state.row_status.copy()
        new_col_status = state.col_status.copy()

        x, y = position
        playerModifier = 1 if player1_turn else -1

        if action_type == 'row':
            new_row_status[y][x] = 1
            if y < len(new_board_status):
                new_board_status[y][x] += playerModifier
            if y > 0:
                new_board_status[y - 1][x] += playerModifier

        elif action_type == 'col':
            new_col_status[y][x] = 1
            if x < len(new_board_status[0]):
                new_board_status[y][x] += playerModifier
            if x > 0:
                new_board_status[y][x - 1] += playerModifier

        return GameState(
            board_status=new_board_status,
            row_status=new_row_status,
            col_status=new_col_status,
            player1_turn=not player1_turn
        )

    def get_possible_actions(self, state: GameState) -> list:
        """
        Return a list of possible actions given the current game state.
        """
        possible_actions = []

        for y in range(len(state.row_status)):
            for x in range(len(state.row_status[0])):
                if state.row_status[y][x] == 0:
                    possible_actions.append(GameAction('row', (x, y)))

        for y in range(len(state.col_status)):
            for x in range(len(state.col_status[0])):
                if state.col_status[y][x] == 0:
                    possible_actions.append(GameAction('col', (x, y)))

        return possible_actions

    def is_terminal(self, state: GameState) -> bool:
        """
        Check if the game is over.
        """
        return np.all(state.row_status == 1) and np.all(state.col_status == 1)

    def evaluate_terminal_state(self, state: GameState) -> float:
        """
        Evaluate the terminal state and return the game outcome.
        1 for player1 win, -1 for player2 win, and 0 for a tie.
        """
        player1_score = np.sum(state.board_status == 4)
        player2_score = np.sum(state.board_status == -4)

        if player1_score > player2_score:
            return 1
        elif player2_score > player1_score:
            return -1
        else:
            return 0

    def get_player_name(self) -> str:
        return "MCTSPlayer"
