from copy import deepcopy
from typing import List
from numpy import ndarray
from game_action import GameAction

class GameState:
    NUM_OF_DOTS = None
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

        pointsScored = False
        logical_position = action.position
        type = action.action_type
        x = logical_position[0]
        y = logical_position[1]

        val = 1
        playerModifier = 1
        if new_state.player1_turn:
            playerModifier = -1

        if y < (GameState.NUM_OF_DOTS - 1) and x < (GameState.NUM_OF_DOTS - 1):
            new_state.board_status[y][x] = (abs(new_state.board_status[y][x]) + val) * playerModifier
            if abs(new_state.board_status[y][x]) == 4:
                pointsScored = True

        if type == 'row':
            new_state.row_status[y][x] = 1
            if y >= 1:
                new_state.board_status[y - 1][x] = (abs(new_state.board_status[y - 1][x]) + val) * playerModifier
                if abs(new_state.board_status[y - 1][x]) == 4:
                    pointsScored = True

        elif type == 'col':
            new_state.col_status[y][x] = 1
            if x >= 1:
                new_state.board_status[y][x - 1] = (abs(new_state.board_status[y][x - 1]) + val) * playerModifier
                if abs(new_state.board_status[y][x - 1]) == 4:
                    pointsScored = True

        new_state.player1_turn = (not new_state.player1_turn) if not pointsScored else new_state.player1_turn
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

