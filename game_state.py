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
        self.chain_lengths = []  # Track chain lengths
        self.independents = []  # Independent chains/loops
        self.independents_are_loops = False  # Are the independents loops?
        self.looney_value = 0  # Looney state (0, 2, or 4)
        self.who_to_play_next = player1_turn  # Next player turn
        self.score_so_far = 0  # Net score difference (P1 - P2)

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


    def get_valid_moves(self, state: 'GameState'):
        valid_moves = []
        for x in range(state.row_status.shape[1]):
            for y in range(state.row_status.shape[0]):
                if state.row_status[y, x] == 0:
                    valid_moves.append(GameAction("row", (x, y)))
        for x in range(state.col_status.shape[1]):
            for y in range(state.col_status.shape[0]):
                if state.col_status[y, x] == 0:
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

    def evaluate_looney_state(self):
        one_edge_boxes = self.get_boxes_with_one_unclaimed_edge()

        if len(one_edge_boxes) == 0:
            # No boxes with only 1 edge left, Looney Value is 0
            self.looney_value = 0
        elif len(one_edge_boxes) == 1:
            x, y = one_edge_boxes[0]
            if self.is_part_of_chain(x, y) and self.get_chain_length(x, y) == 3:
                # One box with one edge left, part of a chain of length 3
                self.looney_value = 2
            elif self.is_part_of_loop(x, y) and self.get_loop_length(x, y) == 4:
                # One box with one edge left, part of a loop with 4 boxes remaining
                self.looney_value = 4
        else:
            # Multiple boxes with one edge left do not fall into Looney Value categories
            self.looney_value = 0

    def get_boxes_with_one_unclaimed_edge(self):
        """Find all boxes that have exactly one unclaimed edge."""
        one_edge_boxes = []
        for y in range(self.board_status.shape[0]):
            for x in range(self.board_status.shape[1]):
                if abs(self.board_status[y, x]) == 3:  # 3 claimed edges, 1 unclaimed
                    one_edge_boxes.append((x, y))
        return one_edge_boxes

    def is_part_of_chain(self, x, y) -> bool:
        """Check if the box at (x, y) is part of a chain."""
        return abs(self.board_status[y, x]) == 2  # Chain typically has 2 claimed edges per box

    def get_chain_length(self, x, y) -> int:
        """Return the length of the chain the box is part of."""
        visited = set()
        return self.explore_structure_length(x, y, visited, structure_type='chain')

    def is_part_of_loop(self, x, y) -> bool:
        """Check if the box at (x, y) is part of a loop."""
        return abs(self.board_status[y, x]) == 3  # Loop typically has 3 claimed edges per box

    def get_loop_length(self, x, y) -> int:
        """Return the length of the loop the box is part of."""
        visited = set()
        return self.explore_structure_length(x, y, visited, structure_type='loop')

    def explore_structure_length(self, x, y, visited, structure_type: str) -> int:
        """Helper function to explore the length of a chain or loop starting from (x, y)."""
        length = 0
        stack = [(x, y)]

        while stack:
            current_x, current_y = stack.pop()
            if (current_x, current_y) not in visited:
                visited.add((current_x, current_y))
                length += 1

                # Check neighboring boxes to continue the chain or loop
                neighbors = self.get_structure_neighbors(current_x, current_y, structure_type)
                stack.extend(neighbors)

        return length

    def get_structure_neighbors(self, x, y, structure_type: str):
        """Find neighboring boxes that are part of the same structure (chain or loop)."""
        neighbors = []
        # Check all possible neighboring boxes (above, below, left, right)
        if structure_type == 'chain':
            if y > 0 and self.is_part_of_chain(x, y - 1):  # Above
                neighbors.append((x, y - 1))
            if y < self.board_status.shape[0] - 1 and self.is_part_of_chain(x, y + 1):  # Below
                neighbors.append((x, y + 1))
            if x > 0 and self.is_part_of_chain(x - 1, y):  # Left
                neighbors.append((x - 1, y))
            if x < self.board_status.shape[1] - 1 and self.is_part_of_chain(x + 1, y):  # Right
                neighbors.append((x + 1, y))
        elif structure_type == 'loop':
            if y > 0 and self.is_part_of_loop(x, y - 1):  # Above
                neighbors.append((x, y - 1))
            if y < self.board_status.shape[0] - 1 and self.is_part_of_loop(x, y + 1):  # Below
                neighbors.append((x, y + 1))
            if x > 0 and self.is_part_of_loop(x - 1, y):  # Left
                neighbors.append((x - 1, y))
            if x < self.board_status.shape[1] - 1 and self.is_part_of_loop(x + 1, y):  # Right
                neighbors.append((x + 1, y))
        return neighbors
