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
                return (j,i), 'row'

            # Bottom horizontal line (from row_status)
            bottom_line = state.row_status[i+1][j]
            if bottom_line == 0:
                return (j,i+1), 'row'

            # Left vertical line (from col_status)
            left_line = state.col_status[i][j]
            if left_line == 0:
                return (j,i), 'col'

            # Right vertical line (from col_status)
            right_line = state.col_status[i][j+1]
            if right_line == 0:
                return (j+1,i), 'col'

    def get_action(self, state: GameState) -> GameAction:
        free_box = self.check_for_free_boxes(state)
        if free_box:
            return GameAction(free_box[1], free_box[0])

        # Start Alpha-Beta Minimax
        best_score, best_action = self.alpha_beta_search(state, self.depth, -math.inf, math.inf, True)
        print(f"Best score: {best_score}")
        return best_action

    def get_player_name(self) -> str:
        return "AlphaBetaPlayer"

    def alpha_beta_search(self, state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool):
        if depth == 0 or state.is_gameover():
            return self.evaluate(state), None

        valid_moves = state.get_valid_moves(state)
        best_move = None

        if maximizing_player:
            max_eval = -math.inf
            for action in valid_moves:
                new_state = state.generate_successor(action)
                eval_score, _ = self.alpha_beta_search(new_state, depth - 1, alpha, beta, False)
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
                eval_score, _ = self.alpha_beta_search(new_state, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = action
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def nearly_completed_boxes(self, state: GameState):
        # Penalty for creating boxes with 3 lines that the opponent can close
        penalty = 0
        for i in range(state.board_status.shape[0]):
            for j in range(state.board_status.shape[1]):
                if state.board_status[i][j] == 3:  # Box with 3 lines
                    penalty += 1  # Apply penalty for leaving a box that opponent can complete

        # If it's Player 1's turn, add penalty, else subtract it
        if state.player1_turn:
            return 0 - penalty
        else:
            return penalty

    def score_diff(self, state: GameState):
        player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
        player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
        return player1_score - player2_score

    def evaluate(self, state: GameState):
        score_diff = self.score_diff(state)
        nearly_completed_boxes = self.nearly_completed_boxes(state)
        return score_diff + len(state.board_status)**2 * nearly_completed_boxes



