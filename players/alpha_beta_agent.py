import random
from players.player import Player
from game_action import GameAction
from game_state import GameState
import math
import heurestics


class AlphaBetaPlayer(Player):
    def __init__(self, depth=3, evaluate=heurestics.score_diff):
        self.depth = depth
        self.evaluate = evaluate

    def get_action(self, state: GameState) -> GameAction:
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
