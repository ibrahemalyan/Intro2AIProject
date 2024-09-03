from numpy import ndarray

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
