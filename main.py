import argparse

from players.expectimax_agent import ExpectimaxPlayer
from players.monte_carlo_agent import MCTSPlayer
from players.qlearning_agent import QLearningAgent
from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from Renderers.gui_renderer import GUI_Renderer
from Renderers.console_renderer import ConsoleRenderer
from players.alpha_beta_agent import AlphaBetaPlayer
from players.human_player import HumanPlayer
from players.newAlphaBeta import NewAlphaBetaPlayer


def create_player(player_name, renderer=None, load_q_table=False):
    if player_name == "RandomPlayer":
        return RandomPlayer()
    elif player_name == "AlphaBetaPlayer":
        return AlphaBetaPlayer()
    elif player_name == "ExpectimaxPlayer":
        return ExpectimaxPlayer()
    elif player_name == "MCTSPlayer":
        return MCTSPlayer()
    elif player_name == "QLearningAgent":
        return QLearningAgent(load_q_table=load_q_table)  # Load Q-table if needed
    elif player_name == "HumanPlayer":
        return HumanPlayer(renderer)
    elif player_name == "pro":
        return NewAlphaBetaPlayer()
    else:
        raise ValueError(f"Invalid player name: {player_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dots and Boxes")
    parser.add_argument("-d", "--number_of_dots", type=int, required=True)
    parser.add_argument("-n", "--games_num", type=int, required=True)
    parser.add_argument("-p1", "--player_1", required=True,
                        help="Choose from: RandomPlayer, AlphaBetaPlayer, ExpectimaxPlayer, MCTSPlayer, QLearningAgent, HumanPlayer")
    parser.add_argument("-p2", "--player_2", required=True,
                        help="Choose from: RandomPlayer, AlphaBetaPlayer, ExpectimaxPlayer, MCTSPlayer, QLearningAgent, HumanPlayer")
    parser.add_argument("--gui", action="store_true", help="Enable GUI renderer instead of console")
    parser.add_argument("--load_q_table", action="store_true", help="Load Q-table for QLearningAgent")

    args = parser.parse_args()

    number_of_dots = args.number_of_dots
    games_num = args.games_num

    if args.gui:
        renderer = GUI_Renderer(number_of_dots)
    else:
        renderer = ConsoleRenderer(number_of_dots)

    score1 = 0
    score2 = 0
    tie = 0

    for i in range(games_num):
        print("Round:", i + 1)
        player1 = create_player(args.player_1, renderer, load_q_table=args.load_q_table)
        player2 = create_player(args.player_2, renderer, load_q_table=args.load_q_table)

        game_instance = Dots_and_Boxes(renderer=renderer, games_num=1, number_of_dots=number_of_dots,
                                       player1=player1, player2=player2)
        game_instance.play()

        score1 += game_instance.get_player1_score()
        score2 += game_instance.get_player2_score()
        tie += game_instance.get_tie()

        if isinstance(player1, QLearningAgent):
            result = 'win' if score1 > score2 else 'loss' if score1 < score2 else 'tie'
            player1.end_game(result)
        if isinstance(player2, QLearningAgent):
            result = 'win' if score2 > score1 else 'loss' if score2 < score1 else 'tie'
            player2.end_game(result)
        print("---------------------------------------------------------------------------")

    print("---------------------------------------------------------------------------")
    print("Final Results:")
    print(f"Player 1 ({args.player_1}): {score1}")
    print(f"Player 2 ({args.player_2}): {score2}")
    print(f"Tie: {tie}")
