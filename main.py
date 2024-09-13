import argparse as argparse

from players.expectimax_agent import ExpectimaxPlayer
from players.monte_carlo_agent import MCTSPlayer
from players.qlearning_agent import QLearningAgent
from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from Renderers.gui_renderer import GUI_Renderer
from Renderers.console_renderer import ConsoleRenderer
from players.alpha_beta_agent import AlphaBetaPlayer


def create_player(player_name,renderer=None):
    if player_name == "RandomPlayer":
        return RandomPlayer()
    elif player_name == "AlphaBetaPlayer":
        return AlphaBetaPlayer()
    elif player_name == "ExpectimaxPlayer":
        return ExpectimaxPlayer()
    elif player_name == "MCTSPlayer":
        return MCTSPlayer()
    elif player_name == "QLearningAgent":
        return QLearningAgent()
    elif player_name == "HumanPlayer":
        return GUI_Renderer(renderer)
    else:
        raise ValueError("Invalid player name")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dots and Boxes")
    parser.add_argument("-d", "--number_of_dots", type=int)
    parser.add_argument("-n", "--games_num", type=int)
    parser.add_argument("-p1", "--player_1",
                        help="Choose from: RandomPlayer, AlphaBetaPlayer, ExpectimaxPlayer, MCTSPlayer, QLearningAgent")
    parser.add_argument("-p2", "--player_2",
                        help="Choose from: RandomPlayer, AlphaBetaPlayer, ExpectimaxPlayer, MCTSPlayer, QLearningAgent")
    args = parser.parse_args()

    number_of_dots = args.number_of_dots
    games_num = args.games_num
    # renderer = GUI_Renderer(number_of_dots, True)
    renderer = ConsoleRenderer(number_of_dots)
    # player1 = HumanPlayer(renderer)
    score1 = 0
    score2 = 0
    tie = 0

    for i in range(games_num):
        player1 = AlphaBetaPlayer()
        player2 = ExpectimaxPlayer()
        game_instance = Dots_and_Boxes(renderer=renderer, games_num=1, number_of_dots=number_of_dots,
                                       player1=create_player(args.player_1,renderer), player2=create_player(args.player_2,renderer))
        game_instance.play()
        score1 += game_instance.get_player1_score()
        score2 += game_instance.get_player2_score()
        tie += game_instance.get_tie()
    print("---------------------------------------------------------------------------")
    print("Final Results:")
    print(f"Player 1 {args.player_1}: {score1}")
    print(f"Player 2 {args.player_2}: {score2}")
    print(f"Tie: {tie}")
