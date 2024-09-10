from players.expectimax_agent import ExpectimaxPlayer
from players.monte_carlo_agent import MCTSPlayer
from players.qlearning_agent import QLearningAgent
from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from Renderers.gui_renderer import GUI_Renderer
from Renderers.console_renderer import ConsoleRenderer
from players.alpha_beta_agent import AlphaBetaPlayer

if __name__ == "__main__":
    number_of_dots = 5
    games_num = 1
    # renderer = GUI_Renderer(number_of_dots, True)
    renderer = ConsoleRenderer(number_of_dots)
    # player1 = HumanPlayer(renderer)
    score1 = 0
    score2 = 0
    tie = 0

    for i in range(10):
        player1 = AlphaBetaPlayer()
        player2 = RandomPlayer()
        game_instance = Dots_and_Boxes(renderer=renderer, games_num=games_num, number_of_dots=number_of_dots,
                                       player1=player1, player2=player2)
        game_instance.play()
        score1 += game_instance.get_player1_score()
        score2 += game_instance.get_player2_score()
        tie += game_instance.get_tie()
    print(f"Player 1: {score1}")
    print(f"Player 2: {score2}")
    print(f"Tie: {tie}")
