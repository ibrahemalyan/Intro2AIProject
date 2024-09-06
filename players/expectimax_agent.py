import numpy as np
import random

from game_state import GameState
from players.player import Player
from game_action import GameAction
from typing import Tuple, List
import math


class ExpectimaxPlayer(Player):
    def __init__(self, max_depth=3):
        super().__init__()
        self.max_depth = max_depth

    def get_action(self, state: GameState) -> GameAction:
        # Start the Expectimax search from the root (current game state)
        best_action, _ = self.expectimax(state, self.max_depth, maximizing_player=True)
        return best_action

    def expectimax(self, state: GameState, depth: int, maximizing_player: bool):
        """
        Expectimax algorithm: recursively explore the game tree.
        - If it's the maximizing player's turn, pick the move with the highest value.
        - If it's the opponent's or chance node, take the expected value of all possible moves.
        """
        if depth == 0 or self.is_terminal(state):
            return None, self.evaluate(state)

        possible_actions = self.get_possible_actions(state)

        if maximizing_player:
            # Max node: Choose the move with the highest value
            max_value = -math.inf
            best_action = None
            for action_type, position in possible_actions:
                new_state = self.simulate_action(state, action_type, position, maximizing_player=True)
                _, value = self.expectimax(new_state, depth - 1, maximizing_player=False)
                if value > max_value:
                    max_value = value
                    best_action = GameAction(action_type, position)
            return best_action, max_value

        else:
            # Chance node: Take the expected value of all possible outcomes
            total_value = 0
            for action_type, position in possible_actions:
                new_state = self.simulate_action(state, action_type, position, maximizing_player=False)
                _, value = self.expectimax(new_state, depth - 1, maximizing_player=True)
                total_value += value
            average_value = total_value / len(possible_actions)
            return None, average_value

    def simulate_action(self, state: GameState, action_type: str, position: Tuple[int, int],
                        maximizing_player: bool) -> GameState:
        """
        Simulate taking an action in the current state. This function returns a new game state.
        """
        new_board_status = state.board_status.copy()
        new_row_status = state.row_status.copy()
        new_col_status = state.col_status.copy()

        x, y = position
        playerModifier = 1 if maximizing_player else -1

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
            player1_turn=not state.player1_turn
        )

    def get_possible_actions(self, state: GameState) -> List[Tuple[str, Tuple[int, int]]]:
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

    def is_terminal(self, state: GameState) -> bool:
        """
        Check if the game is over.
        """
        return np.all(state.row_status == 1) and np.all(state.col_status == 1)

    def evaluate(self, state: GameState) -> float:
        """
        Evaluates the game state. Positive values favor the maximizing player (Player 1),
        while negative values favor the minimizing player (Player 2).
        """
        player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
        player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
        return player1_score - player2_score

    def get_player_name(self) -> str:
        return "ExpectimaxPlayer"
