import numpy as np
from game_state import GameState
from Renderers.renderer import Renderer
from players.player import Player

class Dots_and_Boxes():
    def __init__(self, renderer: Renderer, games_num=100, number_of_dots=4, player1: Player = None,
                 player2: Player = None):
        self.player_wait_time = 1
        self.number_of_dots = number_of_dots
        self.renderer = renderer
        self.player1_starts = True
        self.renderer.refresh_board()
        self.games_num = games_num
        self.player1 = player1
        self.player2 = player2
        self.winner_scores = {f"player1_{player1.get_player_name()}": 0,
                              f"player2_{player2.get_player_name()}": 0, "tie": 0}
        self.first_match = True

    def play(self):
        if self.games_num <= 0:
            self.renderer.display_final_score(self.winner_scores)
            return
        self.games_num -= 1
        self.board_status = np.zeros(shape=(self.number_of_dots - 1, self.number_of_dots - 1))
        self.row_status = np.zeros(shape=(self.number_of_dots, self.number_of_dots - 1))
        self.col_status = np.zeros(shape=(self.number_of_dots - 1, self.number_of_dots))
        self.pointsScored = False

        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []

        self.already_marked_boxes = []
        self.renderer.display_turn_text(1 if self.player1_turn else 2)
        self.turn()
        if self.first_match:
            self.renderer.mainloop()
            self.first_match = False

    def is_grid_occupied(self, logical_position, type):
        x = logical_position[0]
        y = logical_position[1]
        occupied = True

        if type == 'row' and self.row_status[y][x] == 0:
            occupied = False
        if type == 'col' and self.col_status[y][x] == 0:
            occupied = False

        return occupied


    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) !=[]:
                self.already_marked_boxes.append(list(box))
                self.renderer.shade_box(box, 1)

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) !=[]:
                self.already_marked_boxes.append(list(box))
                self.renderer.shade_box(box, 2)

    def update_board(self, type, logical_position):
        x = logical_position[0]
        y = logical_position[1]
        val = 1
        playerModifier = 1
        if self.player1_turn:
            playerModifier = -1
        if y < (self.number_of_dots-1) and x < (self.number_of_dots-1):
            self.board_status[y][x] = (abs(self.board_status[y][x]) + val) * playerModifier
            if abs(self.board_status[y][x]) == 4:
                self.pointsScored = True

        if type == 'row':
            self.row_status[y][x] = 1
            if y >= 1:
                self.board_status[y-1][x] = (abs(self.board_status[y-1][x]) + val) * playerModifier
                if abs(self.board_status[y-1][x]) == 4:
                    self.pointsScored = True

        elif type == 'col':
            self.col_status[y][x] = 1
            if x >= 1:
                self.board_status[y][x-1] = (abs(self.board_status[y][x-1]) + val) * playerModifier
                if abs(self.board_status[y][x-1]) == 4:
                    self.pointsScored = True
    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()

    def click(self, event):
        current_player = self.player1 if self.player1_turn else self.player2
        action = current_player.get_action(event)
        self.update(action.action_type, action.position)

    def update(self, valid_input, logical_position):
        if valid_input and not self.is_grid_occupied(logical_position, valid_input):
            self.update_board(valid_input, logical_position)
            self.renderer.make_edge(valid_input, logical_position, 1 if self.player1_turn else 2)
            self.mark_box()
            self.renderer.refresh_board()
            self.player1_turn = (not self.player1_turn) if not self.pointsScored else self.player1_turn
            self.pointsScored = False

            if self.is_gameover():
                player1_score = len(np.argwhere(self.board_status == -4))
                player2_score = len(np.argwhere(self.board_status == 4))
                if player1_score > player2_score:
                    self.winner_scores[f"player1_{self.player1.get_player_name()}"] += 1
                elif player2_score > player1_score:
                    self.winner_scores[f"player2_{self.player2.get_player_name()}"] += 1
                else:
                    self.winner_scores["tie"] += 1
                self.renderer.restart_game(player1_score, player2_score)
                self.play()
            else:
                self.renderer.display_turn_text(1 if self.player1_turn else 2)
                self.turn()

    def turn(self):
        current_player = self.player1 if self.player1_turn else self.player2
        if current_player.is_clickable():
            self.renderer.window_bind(self.click)
        else:
            self.renderer.window_scheduler(self.player_wait_time, self.player_turn, current_player)


    def player_turn(self, player: Player):
        action = player.get_action(GameState(
            self.board_status.copy(),
            self.row_status.copy(),
            self.col_status.copy(),
            self.player1_turn
        ))
        self.update(action.action_type, action.position)