from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from game_renderer import GameRenderer
from players.human_player import HumanPlayer
from players.qlearning_agent import QLearningAgent
from players.alpha_beta_agent import AlphaBetaPlayer



if __name__ == "__main__":
    number_of_dots = 8
    games_num = 1
    renderer = GameRenderer(number_of_dots, True)
    # player1 = HumanPlayer(renderer)
    player1 = RandomPlayer()
    player2 = RandomPlayer()
    game_instance = Dots_and_Boxes(renderer=renderer,games_num=games_num,number_of_dots=number_of_dots,
                                   player1=player1, player2=player2)
    game_instance.play()
