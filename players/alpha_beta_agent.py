import numpy as np
from game_state import GameState
from players.player import Player
from game_action import GameAction


class AlphaBetaAgent(Player):
    def __init__(self, depth=3):
        self.depth = depth

    def get_player_name(self):
        return "Alpha-Beta Player"

    def get_action(self, state: GameState) -> GameAction:
        best_action = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for action in self.get_all_possible_actions_legal(state):
            value = self.alpha_beta(self.result(state, action), self.depth, alpha, beta, False)
            if value > best_value:
                best_value = value
                best_action = action
            alpha = max(alpha, best_value)

        return best_action

    def alpha_beta(self, state: GameState, depth: int, alpha: float, beta: float, is_maximizing: bool):
        if self.is_terminal(state) or depth == 0:
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
        """
        A more sophisticated evaluation function to guide the Alpha-Beta Player.
        Heuristic considers:
        - Number of boxes completed by each player
        - The number of safe moves (moves that don't complete a box)
        - Avoiding chain formation
        """
        # Scoring
        player1_score = len(np.argwhere(state.board_status == -4))
        player2_score = len(np.argwhere(state.board_status == 4))

        # Safe moves (moves that don't complete a box immediately)
        safe_moves_p1 = self.count_safe_moves(state, True)
        safe_moves_p2 = self.count_safe_moves(state, False)

        # Chain formation (penalize positions where opponent can form chains)
        chain_potential_p1 = self.chain_potential(state, True)
        chain_potential_p2 = self.chain_potential(state, False)

        # Heuristic: maximize score while considering safe moves and avoiding chain formations
        score = (player1_score - player2_score) * 10  # Prioritize box control
        safe_move_balance = (safe_moves_p1 - safe_moves_p2) * 2  # Prefer safe moves
        chain_penalty = (chain_potential_p2 - chain_potential_p1) * 5  # Avoid giving opponent chain opportunities

        return score + safe_move_balance - chain_penalty

    def count_safe_moves(self, state: GameState, is_player1_turn: bool):
        """
        Counts the number of safe moves for the player.
        A safe move is a move that doesn't result in completing a box.
        """
        safe_moves = 0
        for action in self.get_all_possible_actions_legal(state):
            new_state = self.result(state, action)
            if not self.did_complete_box(state, new_state, is_player1_turn):
                safe_moves += 1
        return safe_moves

    def did_complete_box(self, old_state: GameState, new_state: GameState, is_player1_turn: bool):
        """
        Check if a box was completed as a result of the move.
        """
        old_score = len(np.argwhere(old_state.board_status == (-4 if is_player1_turn else 4)))
        new_score = len(np.argwhere(new_state.board_status == (-4 if is_player1_turn else 4)))
        return new_score > old_score

    def chain_potential(self, state: GameState, is_player1_turn: bool):
        """
        Calculate chain potential by counting the number of nearly completed boxes
        for the opponent.
        """
        potential_chains = 0
        for y in range(state.board_status.shape[0]):
            for x in range(state.board_status.shape[1]):
                box_value = state.board_status[y][x]
                if abs(box_value) == 3:  # Nearly completed box
                    potential_chains += 1
        return potential_chains

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
        """
        Simulates the action and returns the new state.
        """
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
        elif action.action_type == 'col':
            new_state.col_status[y][x] = 1
            if x < new_state.board_status.shape[1]:
                new_state.board_status[y][x] += 1 if new_state.player1_turn else -1
            if x > 0:
                new_state.board_status[y][x - 1] += 1 if new_state.player1_turn else -1

        return new_state
