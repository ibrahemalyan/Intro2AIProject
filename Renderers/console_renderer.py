from Renderers.renderer import Renderer


class ConsoleRenderer(Renderer):
    def __init__(self, number_of_dots=4):
        self.number_of_dots = number_of_dots
        self.player1_score = 0
        self.player2_score = 0

    def refresh_board(self):
        # Initializes the board and prints the starting state
        print(f"Starting a new game with {self.number_of_dots} dots.")


    def display_final_score(self, winner_scores):
        print("Final Results of all games:")
        for key, score in winner_scores.items():
            print(f"{key}: {score}")

    def restart_game(self, player1_score, player2_score):
        print(f"Game ended. Player 1: {player1_score}, Player 2: {player2_score}")


    def display_gameover(self, player1_score, player2_score):
        print("Game over!")
        print(f"Player 1 Score: {player1_score}, Player 2 Score: {player2_score}")

    def update_scores(self, player1_score, player2_score):
        self.player1_score = player1_score
        self.player2_score = player2_score


