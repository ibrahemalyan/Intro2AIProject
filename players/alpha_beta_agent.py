from game_state import GameState
from players.player import Player
from game_action import GameAction
import numpy as np
import math
from typing import Tuple


class AlphaBetaPlayer(Player):
    def __init__(self, max_depth=3):
        super().__init__()
        self.max_depth = max_depth  # The depth of the minimax search

    def get_action(self, state: GameState) -> GameAction:
        best_move, _ = self.alpha_beta_search(state, self.max_depth, -math.inf, math.inf, maximizing_player=True)
        return best_move

    def alpha_beta_search(self, state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool):
        """
        Alpha-beta pruning implementation of minimax.
        """
        if depth == 0 or self.is_terminal(state):
            return None, self.evaluate(state)

        possible_actions = self.get_possible_actions(state)

        if maximizing_player:
            max_eval = -math.inf
            best_action = None
            for action_type, position in possible_actions:
                new_state = self.simulate_action(state, action_type, position, maximizing_player=True)
                _, eval = self.alpha_beta_search(new_state, depth - 1, alpha, beta, maximizing_player=False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = GameAction(action_type, position)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return best_action, max_eval

        else:
            min_eval = math.inf
            best_action = None
            for action_type, position in possible_actions:
                new_state = self.simulate_action(state, action_type, position, maximizing_player=False)
                _, eval = self.alpha_beta_search(new_state, depth - 1, alpha, beta, maximizing_player=True)
                if eval < min_eval:
                    min_eval = eval
                    best_action = GameAction(action_type, position)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return best_action, min_eval

    def simulate_action(self, state: GameState, action_type: str, position: Tuple[int, int], maximizing_player: bool) -> GameState:
        """
        Simulates taking an action in the current state. This function returns a new game state.
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

        new_state = GameState(
            board_status=new_board_status,
            row_status=new_row_status,
            col_status=new_col_status,
            player1_turn=not state.player1_turn
        )

        return new_state

    def get_possible_actions(self, state: GameState) -> list:
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
        Checks if the game is over (all rows and columns are marked).
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
        return "AlphaBetaPlayer"
