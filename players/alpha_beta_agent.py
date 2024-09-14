import random
from typing import Tuple, Literal

from players.player import Player
from game_action import GameAction
from game_state import GameState
import math
import numpy as np


class AlphaBetaPlayer(Player):
    def __init__(self, depth=3):
        self.depth = depth

    def check_for_free_boxes(self, state: GameState) -> Tuple[Tuple[int, int], Literal['row', 'col']]:
        pos = None
        for i, row in enumerate(state.board_status):
            for j, element in enumerate(row):
                if element == 3 or element == -3:
                    pos = (i, j)

        if pos:
            i, j = pos
            # Top horizontal line (from row_status)
            top_line = state.row_status[i][j]
            if top_line == 0:
                return (j, i), 'row'

            # Bottom horizontal line (from row_status)
            bottom_line = state.row_status[i + 1][j]
            if bottom_line == 0:
                return (j, i + 1), 'row'

            # Left vertical line (from col_status)
            left_line = state.col_status[i][j]
            if left_line == 0:
                return (j, i), 'col'

            # Right vertical line (from col_status)
            right_line = state.col_status[i][j + 1]
            if right_line == 0:
                return (j + 1, i), 'col'

    def get_action(self, state: GameState) -> GameAction:
        free_box = self.check_for_free_boxes(state)
        if free_box:
            return GameAction(free_box[1], free_box[0])

        # Start Alpha-Beta Minimax
        score, best_action = self.alpha_beta_search(state, self.depth, -math.inf, math.inf)
        # print(f"Best action: {best_action.position}", f"Score: {score}")
        return best_action

    def get_player_name(self) -> str:
        return "AlphaBetaPlayer"

    def alpha_beta_search(self, state: GameState, depth: int, alpha: float, beta: float):
        if depth == 0 or state.is_gameover():
            return self.evaluate(state), None

        valid_moves = state.get_valid_moves()
        random.shuffle(valid_moves)
        best_move = None

        maximizing_player = state.player1_turn
        if maximizing_player:
            max_eval = -math.inf
            for action in valid_moves:
                new_state = state.generate_successor(action)
                eval_score, _ = self.alpha_beta_search(new_state, depth - 1, alpha, beta)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = action
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for action in valid_moves:
                new_state = state.generate_successor(action)
                eval_score, _ = self.alpha_beta_search(new_state, depth - 1, alpha, beta)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = action
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def score_diff(self, state: GameState):
        player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
        player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
        return  player2_score - player1_score


    def evaluate(self, state: GameState):
        score_diff = self.score_diff(state)
        chain_length_score = self.chain_length_evaluation(state)

        # Combine score difference and chain length score
        total_evaluation = score_diff

        # print(f"Score diff: {score_diff}")
        return total_evaluation

    def chain_length_evaluation(self, state: GameState):
        """
        Evaluate the state by considering the lengths of chains of free boxes.
        Longer chains are rewarded.
        """
        chain_length_score = 0

        # Check each box in the board
        for y in range(state.board_status.shape[0]):
            for x in range(state.board_status.shape[1]):
                if abs(state.board_status[y, x]) == 3:  # Free box with 3 sides
                    chain_length_score += self.detect_chain_length(state, x, y)

        return chain_length_score

    def detect_chain_length(self, state: GameState, x: int, y: int):
        """
        Recursively detect the length of a chain starting from a box with 3 sides.
        A chain is a sequence of boxes that are directly adjacent to each other with only one side missing.
        """
        visited = set()
        return self._chain_length_dfs(state, x, y, visited)

    def _chain_length_dfs(self, state: GameState, x: int, y: int, visited: set):
        if (x, y) in visited:
            return 0
        if abs(state.board_status[y, x]) != 3:
            return 0

        # Mark the box as visited
        visited.add((x, y))

        chain_length = 1  # Start with the current box

        # Check neighboring boxes (up, down, left, right)
        if y > 0:
            chain_length += self._chain_length_dfs(state, x, y - 1, visited)  # up
        if y < state.board_status.shape[0] - 1:
            chain_length += self._chain_length_dfs(state, x, y + 1, visited)  # down
        if x > 0:
            chain_length += self._chain_length_dfs(state, x - 1, y, visited)  # left
        if x < state.board_status.shape[1] - 1:
            chain_length += self._chain_length_dfs(state, x + 1, y, visited)  # right

        return chain_length
