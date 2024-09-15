import random
from typing import Tuple, Literal
import math
from players.player import Player
from game_action import GameAction
from game_state import GameState
import heurestics


class ExpectimaxPlayer(Player):
    def __init__(self, depth=3, evaluate=heurestics.score_diff):
        self.depth = depth
        self.evaluate = evaluate

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

        # Start Expectimax search
        score, best_action = self.expectimax_search(state, self.depth)
        return best_action

    def get_player_name(self) -> str:
        return "ExpectimaxPlayer"

    def expectimax_search(self, state: GameState, depth: int):
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
                eval_score, _ = self.expectimax_search(new_state, depth - 1)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = action
            return max_eval, best_move
        else:
            expected_value = 0
            for action in valid_moves:
                new_state = state.generate_successor(action)
                eval_score, _ = self.expectimax_search(new_state, depth - 1)
                expected_value += eval_score / len(valid_moves)  # Taking the average of all possible outcomes
            return expected_value, None
