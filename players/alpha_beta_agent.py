from typing import Tuple, Literal

import numpy as np
from game_state import GameState
from game_action import GameAction
from players.player import Player


class AlphaBetaPlayer(Player):
    def __init__(self, depth=3):
        super().__init__()
        self.depth = depth

    def get_player_name(self):
        return "Alpha-Beta Player"

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
        best_action = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        free_box = self.check_for_free_boxes(state)
        if free_box:
            print(f"Free box found at {free_box[0]} with action type {free_box[1]}")
            return GameAction(free_box[1], free_box[0])

        for action in self.get_all_possible_actions_legal(state):
            value = self.alpha_beta(self.result(state, action), self.depth, alpha, beta, False)
            if value > best_value:
                best_value = value
                best_action = action
            alpha = max(alpha, best_value)

        return best_action

    def alpha_beta(self, state: GameState, depth: int, alpha: float, beta: float, is_maximizing: bool):
        if  self.is_terminal(state) or depth==0 :
            return self.evaluate(state)

        if is_maximizing:
            max_eval = float('-inf')
            for action in self.get_all_possible_actions_legal(state):
                eval = self.alpha_beta(self.result(state, action), depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for action in self.get_all_possible_actions_legal(state):
                eval = self.alpha_beta(self.result(state, action), depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval

    def evaluate(self, state: GameState):
        # Current score for both players
        player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
        player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
        return player1_score - player2_score

    def is_terminal(self, state: GameState):
        return (state.row_status == 1).all() and (state.col_status == 1).all()

    def get_all_possible_actions_legal(self, state: GameState):
        actions = []
        for y in range(state.row_status.shape[0]):
            for x in range(state.row_status.shape[1]):
                if state.row_status[y][x] == 0:
                    actions.append(GameAction('row', (x, y)))

        for y in range(state.col_status.shape[0]):
            for x in range(state.col_status.shape[1]):
                if state.col_status[y][x] == 0:
                    actions.append(GameAction('col', (x, y)))

        return actions

    def result(self, state: GameState, action: GameAction):
        # Simulate the action and return the new state
        new_state = GameState(
            state.board_status.copy(),
            state.row_status.copy(),
            state.col_status.copy(),
            not state.player1_turn
        )
        x, y = action.position
        if action.action_type == 'row':
            new_state.row_status[y][x] = 1
            if y < new_state.board_status.shape[0]:
                new_state.board_status[y][x] += 1 if new_state.player1_turn else -1
            if y > 0:
                new_state.board_status[y - 1][x] += 1 if new_state.player1_turn else -1
        elif action.action_type =='col':
            new_state.col_status[y][x] = 1
            if x < new_state.board_status.shape[1]:
                new_state.board_status[y][x] += 1 if new_state.player1_turn else -1
            if x > 0:
                new_state.board_status[y][x - 1] += 1 if new_state.player1_turn else -1

        return new_state
