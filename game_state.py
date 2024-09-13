from copy import deepcopy
from typing import List

from numpy import ndarray

from game_action import GameAction


class GameState:
    """
    board_status: int[][]
        counts how many lines from the box where taken. if the answer is not in [4,-4] that means the box
        isn't filled. 4 means it was taken by player1, -4 means it was taken by player2
        Access: board_status[y, x]

    row_status: int[][]
        Represent the horizontal/row lines. value=1 means taken, value=0 means not taken
        Access: row_status[y, x]

    col_status: int[][]
        Represent the vertical/column lines. value=1 means taken, value=0 means not taken
        Access: col_status[y, x]

    player1_turn: bool
        True if it is player 1 turn, False for player 2.
    """
    def __init__(self, board_status: ndarray, row_status: ndarray, col_status: ndarray, player1_turn: bool):
        self.board_status = board_status
        self.row_status = row_status
        self.col_status = col_status
        self.player1_turn = player1_turn

    def generate_successor(self, action: GameAction) -> 'GameState':
        new_state = GameState(
            self.board_status.copy(),
            self.row_status.copy(),
            self.col_status.copy(),
            self.player1_turn
        )
        new_state._apply_action(action)  # Apply the action to update the board
        new_state.player1_turn = not self.player1_turn  # Switch turns
        return new_state

    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()


    def get_valid_moves(self):
        valid_moves = []
        for x in range(self.row_status.shape[1]):
            for y in range(self.row_status.shape[0]):
                if self.row_status[y, x] == 0:
                    valid_moves.append(GameAction("row", (x, y)))
        for x in range(self.col_status.shape[1]):
            for y in range(self.col_status.shape[0]):
                if self.col_status[y, x] == 0:
                    valid_moves.append(GameAction("col", (x, y)))
        return valid_moves

    def _apply_action(self, action: GameAction):
        """
        Apply the action (drawing a row or a column) to the current game state.
        """
        x, y = action.position
        player_modifier = -1 if self.player1_turn else 1
        val = 1

        if action.action_type == "row":
            self.row_status[y][x] = 1
            if y < (self.board_status.shape[0]):
                self.board_status[y][x] = (abs(self.board_status[y][x]) + val) * player_modifier
                if abs(self.board_status[y][x]) == 4:
                    self.pointsScored = True
            if y >= 1:
                self.board_status[y-1][x] = (abs(self.board_status[y-1][x]) + val) * player_modifier
                if abs(self.board_status[y-1][x]) == 4:
                    self.pointsScored = True

        elif action.action_type == "col":
            self.col_status[y][x] = 1
            if x < (self.board_status.shape[1]):
                self.board_status[y][x] = (abs(self.board_status[y][x]) + val) * player_modifier
                if abs(self.board_status[y][x]) == 4:
                    self.pointsScored = True
            if x >= 1:
                self.board_status[y][x-1] = (abs(self.board_status[y][x-1]) + val) * player_modifier
                if abs(self.board_status[y][x-1]) == 4:
                    self.pointsScored = True


