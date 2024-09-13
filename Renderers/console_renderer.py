from Renderers.renderer import Renderer
import time

class ConsoleRenderer(Renderer):

    def __init__(self, number_of_dots=4):
        self.number_of_dots = number_of_dots

    def refresh_board(self):
        # Initializes the board and prints the starting state
        pass

    def display_gameover(self, player1_score, player2_score):
        print(f"Final Scores - Player 1: {player1_score}, Player 2: {player2_score}")

    # def display_final_score(self, winner_scores):
    #     print("Final Results of all games:")
    #     for key, score in winner_scores.items():
    #         print(f"{key}: {score}")

    def restart_game(self, player1_score, player2_score):
        print(f"Game ended. Player 1: {player1_score}, Player 2: {player2_score}")
        self.refresh_board()

    def window_scheduler(self, player_wait_time, player_turn, current_player):
        player_turn(current_player)

