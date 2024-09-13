import numpy as np
from game_state import GameState
from game_action import GameAction
from players.player import Player


class NewAlphaBetaPlayer(Player):
    def __init__(self, depth=3):
        super().__init__()
        self.depth = depth

    def get_player_name(self):
        return "Pro Alpha-Beta Player"

    def get_action(self, state: GameState) -> GameAction:
        # Implement strategy priorities before doing alpha-beta
        if self.is_broken_chain_or_loop(state):
            print()
            return self.take_free_move(state)

        # If no early move is found, proceed with alpha-beta search
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

    def is_broken_chain_or_loop(self, state: GameState) -> bool:
        # Check for broken chains or loops based on the state
        state.evaluate_looney_state()
        # Example: Check if any chains or loops match the criteria
        for chain in state.chain_lengths:
            if chain != 3:  # Handle chain not equal to 3
                return True
        for loop in state.independents:
            if loop > 4:  # Handle loop greater than 4
                return True
        return False

    def take_free_move(self, state: GameState) -> GameAction:
        # Prioritize moves based on the criteria you described
        if any(loop > 4 for loop in state.independents):
            # Eat square from broken loop
            return self.eat_square_from_structure(state, 'loop')
        elif any(chain != 3 for chain in state.chain_lengths):
            # Eat square from broken chain
            return self.eat_square_from_structure(state, 'chain')
        # Add further conditions based on priority

    def evaluate(self, state: GameState) -> int:
        # Adjust evaluation based on Looney Value
        if state.looney_value in [2, 4]:
            return (3 / 4) * state.score_so_far  # Simplified looney evaluation

        player1_score = np.sum(state.board_status == 4)  # Player 1 completed boxes
        player2_score = np.sum(state.board_status == -4)  # Player 2 completed boxes
        return player1_score - player2_score

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
        elif action.action_type == 'col':
            new_state.col_status[y][x] = 1
            if x < new_state.board_status.shape[1]:
                new_state.board_status[y][x] += 1 if new_state.player1_turn else -1
            if x > 0:
                new_state.board_status[y][x - 1] += 1 if new_state.player1_turn else -1

        return new_state

    def eat_square_from_structure(self, state: GameState, structure_type: str) -> GameAction:
        """
        This function will handle both chains and loops.
        :param state: The current game state.
        :param structure_type: Either 'chain' or 'loop'.
        :return: A GameAction representing the move to take.
        """
        # Find the relevant structures (chains or loops)
        structures = self.find_structures(state, structure_type)

        if not structures:
            return None  # No chains or loops found

        # Select the first structure and the first uncompleted box in that structure
        first_structure = structures[0]
        for box_position in first_structure:
            # Get the list of unclaimed edges for this box
            unclaimed_edges = self.get_unclaimed_edges(state, box_position)
            if unclaimed_edges:
                # Take the first unclaimed edge
                return unclaimed_edges[0]

        return None  # Fallback, should never reach here if structures are found

    def find_structures(self, state: GameState, structure_type: str):
        """
        Generalized function to find either chains or loops.
        :param state: The current game state.
        :param structure_type: Either 'chain' or 'loop'.
        :return: List of found structures.
        """
        structures = []
        visited = set()

        for y in range(state.board_status.shape[0]):
            for x in range(state.board_status.shape[1]):
                if (x, y) not in visited and self.is_part_of_structure(state, x, y, structure_type):
                    # Start exploring the structure
                    structure = self.explore_structure(state, x, y, visited, structure_type)
                    if structure:
                        structures.append(structure)
        return structures

    def is_part_of_structure(self, state: GameState, x: int, y: int, structure_type: str) -> bool:
        """
        Checks if a box is part of a structure (chain or loop).
        :param state: The current game state.
        :param x: The x-coordinate of the box.
        :param y: The y-coordinate of the box.
        :param structure_type: Either 'chain' or 'loop'.
        :return: True if the box is part of the specified structure.
        """
        if structure_type == 'chain':
            # A box is part of a chain if it has exactly 2 edges claimed
            return state.board_status[y, x] == 2 or state.board_status[y, x] == -2
        elif structure_type == 'loop':
            # A box is part of a loop if it has exactly 3 edges claimed
            return state.board_status[y, x] == 3 or state.board_status[y, x] == -3
        return False

    def explore_structure(self, state: GameState, x: int, y: int, visited: set, structure_type: str):
        """
        Generalized function to explore either chains or loops.
        :param state: The current game state.
        :param x: The x-coordinate of the starting box.
        :param y: The y-coordinate of the starting box.
        :param visited: Set of already visited boxes.
        :param structure_type: Either 'chain' or 'loop'.
        :return: A list representing the explored structure.
        """
        structure = []
        stack = [(x, y)]

        while stack:
            current_x, current_y = stack.pop()
            if (current_x, current_y) not in visited and self.is_part_of_structure(state, current_x, current_y,
                                                                                   structure_type):
                structure.append((current_x, current_y))
                visited.add((current_x, current_y))
                # Add neighboring boxes that are also part of the structure
                neighbors = self.get_structure_neighbors(state, current_x, current_y, structure_type)
                stack.extend(neighbors)

        return structure

    def get_structure_neighbors(self, state: GameState, x: int, y: int, structure_type: str):
        """
        Finds neighboring boxes that are part of the same structure (chain or loop).
        :param state: The current game state.
        :param x: The x-coordinate of the current box.
        :param y: The y-coordinate of the current box.
        :param structure_type: Either 'chain' or 'loop'.
        :return: List of neighboring boxes that are part of the same structure.
        """
        neighbors = []
        # Check all possible neighboring boxes (above, below, left, right)
        if y > 0 and self.is_part_of_structure(state, x, y - 1, structure_type):  # Above
            neighbors.append((x, y - 1))
        if y < state.board_status.shape[0] - 1 and self.is_part_of_structure(state, x, y + 1,
                                                                             structure_type):  # Below
            neighbors.append((x, y + 1))
        if x > 0 and self.is_part_of_structure(state, x - 1, y, structure_type):  # Left
            neighbors.append((x - 1, y))
        if x < state.board_status.shape[1] - 1 and self.is_part_of_structure(state, x + 1, y,
                                                                             structure_type):  # Right
            neighbors.append((x + 1, y))
        return neighbors

    def get_unclaimed_edges(self, state: GameState, box_position: tuple) -> list:
        """
        Finds the unclaimed edges of a box.
        :param state: The current game state.
        :param box_position: A tuple representing the (x, y) position of the box.
        :return: List of unclaimed edges as GameAction.
        """
        x, y = box_position
        unclaimed_edges = []

        # Check the four possible edges around the box (row above, row below, col left, col right)
        if state.row_status[y][x] == 0:  # Top edge
            unclaimed_edges.append(GameAction('row', (x, y)))
        if y < state.row_status.shape[0] - 1 and state.row_status[y + 1][x] == 0:  # Bottom edge
            unclaimed_edges.append(GameAction('row', (x, y + 1)))
        if state.col_status[y][x] == 0:  # Left edge
            unclaimed_edges.append(GameAction('col', (x, y)))
        if x < state.col_status.shape[1] - 1 and state.col_status[y][x + 1] == 0:  # Right edge
            unclaimed_edges.append(GameAction('col', (x + 1, y)))

        return unclaimed_edges


