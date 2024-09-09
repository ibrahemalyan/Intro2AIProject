from tkinter import *
import numpy as np

class Renderer:

    def mainloop(self):
        pass

    def display_scores(self):
        pass

    def convert_grid_to_logical_position(self, grid_position):
        pass

    def shade_box(self, box, player):
        pass

    def make_edge(self, type, logical_position, player_turn):
        pass

    def display_gameover(self, player1_score, player2_score):
        pass

    def refresh_board(self):
        pass

    def refresh_window(self, func):
        pass

    def display_turn_text(self, player):
        pass

    def restart_game(self, player1_score, player2_score):
        pass

    def display_final_score(self, winner_scores):
        pass

    def window_scheduler(self,player_wait_time,player_turn, current_player):
        pass

    def window_bind(self,click):
        pass