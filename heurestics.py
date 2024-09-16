from game_state import GameState
import numpy as np
from typing import Tuple, Literal


def is_endgame(state: GameState):
    for i, row in enumerate(state.board_status):
        for j, element in enumerate(row):
            if element == 1 or element == -1:
                return False
    return True


def backCross(state: GameState):
    score = score_diff(state)
    chain_length_score = chain_len(state)

    if chain_len(state, start_box=3) == 1 and chain_len(state, start_box=2) >= 1 and is_endgame(state):
        return 1000
    # if is_endgame(state):
    #     return score + chain_len(state, start_box=2)
    return score



def check_for_free_boxes(state: GameState):
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


def score_diff(state: GameState):
    player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
    player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
    print(player1_score - player2_score)
    return player1_score - player2_score


def chain_length_evaluation(state: GameState):
    """
    Evaluate the state by considering the lengths of chains of free boxes.
    Longer chains are rewarded, but avoid creating short chains too early.
    """
    if chain_len(state):
        return 0


def double_cross_evaluation(state: GameState):
    """
    Evaluate the board for double-cross potential, i.e., forcing the opponent
    to complete an unfavorable move.
    """
    double_cross_score = 0

    # Scan for chains that can be delayed to set up a double-cross
    for y in range(state.board_status.shape[0]):
        for x in range(state.board_status.shape[1]):
            if abs(state.board_status[y, x]) == 3:  # Free box with 3 sides
                # Check if this move could be delayed to force the opponent into a bad chain
                if is_chain_opportunity(state, x, y):
                    double_cross_score += 5  # Reward setting up double-cross opportunities

    return double_cross_score


def detect_chain_length(state: GameState, x: int, y: int):
    visited = set()
    return _chain_length_dfs(state, x, y, visited)


def _chain_length_dfs(state: GameState, x: int, y: int, visited: set):
    if (x, y) in visited or abs(state.board_status[y, x]) != 3:
        return 0

    visited.add((x, y))
    chain_length = 1  # Start with the current box

    # Check neighboring boxes (up, down, left, right)
    if y > 0:
        chain_length += _chain_length_dfs(state, x, y - 1, visited)  # up
    if y < state.board_status.shape[0] - 1:
        chain_length += _chain_length_dfs(state, x, y + 1, visited)  # down
    if x > 0:
        chain_length += _chain_length_dfs(state, x - 1, y, visited)  # left
    if x < state.board_status.shape[1] - 1:
        chain_length += _chain_length_dfs(state, x + 1, y, visited)  # right

    return chain_length


def is_chain_opportunity(state: GameState, x: int, y: int):
    """
    Determine if delaying this box will create a forced chain for the opponent.
    """
    # A simplified check: return True if there are neighboring boxes that are also close to forming chains
    neighboring_chains = 0

    if y > 0 and abs(state.board_status[y - 1][x]) == 3:
        neighboring_chains += 1
    if y < state.board_status.shape[0] - 1 and abs(state.board_status[y + 1][x]) == 3:
        neighboring_chains += 1
    if x > 0 and abs(state.board_status[y][x - 1]) == 3:
        neighboring_chains += 1
    if x < state.board_status.shape[1] - 1 and abs(state.board_status[y][x + 1]) == 3:
        neighboring_chains += 1

    return neighboring_chains >= 2  # Consider it an opportunity if 2 or more neighboring chains exist


def is_chain_of_2s(state, y, x, prev_y, prev_x):
    """Check if the box at position (y, x) has exactly 2 sides filled."""
    return abs(state.board_status[y][x]) == 2 and check_common_line_between_boxes(state, y, x, prev_y, prev_x)


def check_common_line_between_boxes(game_state: GameState, y1: int, x1: int, y2: int, x2: int) -> bool:
    """
    Checks if there's a common line between two adjacent boxes at coordinates (y1, x1) and (y2, x2).
    """
    if y1 == y2:  # Boxes are horizontally adjacent
        if x1 < x2:
            return game_state.col_status[y1, x1] == 1  # Check the vertical line on the right
        elif x1 > x2:
            return game_state.col_status[y1, x2] == 1  # Check the vertical line on the left
    elif x1 == x2:  # Boxes are vertically adjacent
        if y1 < y2:
            return game_state.row_status[y1, x1] == 1  # Check the horizontal line below
        elif y1 > y2:
            return game_state.row_status[y2, x1] == 1  # Check the horizontal line above

    return False


def chain_len(game_state: GameState, start_box=3) -> int:
    rows, cols = game_state.board_status.shape
    visited = [[False for _ in range(cols)] for _ in range(rows)]

    def dfs(y, x):
        """Perform DFS to calculate the length of the chain starting from box (y, x)."""
        stack = [(y, x)]
        chain_length = 0

        while stack:
            cur_y, cur_x = stack.pop()
            if visited[cur_y][cur_x]:
                continue

            visited[cur_y][cur_x] = True
            chain_length += 1

            # Explore neighbors (up, down, left, right) that are part of the same chain of 2s
            neighbors = []
            if cur_y > 0 and not visited[cur_y - 1][cur_x] and is_chain_of_2s(game_state, cur_y - 1, cur_x, cur_y,
                                                                              cur_x):
                neighbors.append((cur_y - 1, cur_x))  # up
            if cur_y < rows - 1 and not visited[cur_y + 1][cur_x] and is_chain_of_2s(game_state, cur_y + 1, cur_x,
                                                                                     cur_y, cur_x):
                neighbors.append((cur_y + 1, cur_x))  # down
            if cur_x > 0 and not visited[cur_y][cur_x - 1] and is_chain_of_2s(game_state, cur_y, cur_x - 1, cur_y,
                                                                              cur_x):
                neighbors.append((cur_y, cur_x - 1))  # left
            if cur_x < cols - 1 and not visited[cur_y][cur_x + 1] and is_chain_of_2s(game_state, cur_y, cur_x + 1,
                                                                                     cur_y, cur_x):
                neighbors.append((cur_y, cur_x + 1))  # right

            stack.extend(neighbors)

        return chain_length

    longest_chain = 0

    for y in range(rows):
        for x in range(cols):
            if not visited[y][x] and abs(game_state.board_status[y][x]) == 3:
                chain_length = dfs(y, x)
                longest_chain = max(longest_chain, chain_length)

    return longest_chain
