import argparse
import os
import pickle

from players.expectimax_agent import ExpectimaxPlayer
from players.monte_carlo_agent import MCTSPlayer
from players.qlearning_agent import QLearningAgent
from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from Renderers.gui_renderer import GUI_Renderer
from Renderers.console_renderer import ConsoleRenderer
from players.alpha_beta_agent import AlphaBetaPlayer
from players.human_player import HumanPlayer
import heurestics
from game_state import GameState


def create_player(player_name, heurestic, depth=3, renderer=None, load_q_table=False):
    if player_name == "Random":
        return RandomPlayer()
    elif player_name == "AlphaBeta":
        return AlphaBetaPlayer(evaluate=heurestic, depth=depth)
    elif player_name == "Expectimax":
        return ExpectimaxPlayer()
    elif player_name == "MCTS":
        return MCTSPlayer()
    elif player_name == "QLearning":
        return QLearningAgent(load_q_table=load_q_table)  # Load Q-table if needed
    elif player_name == "Human":
        return HumanPlayer(renderer)
    else:
        raise ValueError(f"Invalid player name: {player_name}")


def get_heurestic(hereustic):
    if hereustic == "score_diff":
        return heurestics.score_diff
    elif hereustic == "back_cross":
        return heurestics.backCross
    else:
        raise ValueError(f"Invalid hereustic name: {hereustic}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dots and Boxes")
    parser.add_argument("-d", "--number_of_dots", type=int, default=4)
    parser.add_argument("-n", "--games_num", type=int, default=10)
    parser.add_argument("-p1", "--player_1", required=True,
                        help="Choose from: Random, AlphaBeta, Expectimax, MCTS, QLearning, Human")
    parser.add_argument("-p2", "--player_2", required=True,
                        help="Choose from: Random, AlphaBeta, Expectimax, MCTS, QLearning, Human")
    parser.add_argument('-h1', "--heuristic_1", default='score_diff', help="Choose from: score_diff, back_cross")
    parser.add_argument('-h2', "--heuristic_2", default='score_diff', help="Choose from: score_diff, back_cross")
    parser.add_argument("--gui", action="store_true", help="Enable GUI renderer instead of console")
    parser.add_argument("--load_q_table", default=None, help="Load Q-table for QLearningAgent")
    parser.add_argument("--eval", action="store_true", help="save the results while training")
    parser.add_argument("--depth", type=int, default=3, help="file to save the results")

    args = parser.parse_args()
    number_of_dots = args.number_of_dots
    GameState.NUM_OF_DOTS = number_of_dots
    games_num = args.games_num

    if args.gui:
        renderer = GUI_Renderer(number_of_dots)
    else:
        renderer = ConsoleRenderer(number_of_dots)

    score1 = 0
    score2 = 0
    tie = 0

    if args.eval:
        if os.path.exists('eval_data.pkl'):
            with open('eval_data.pkl', 'rb') as file:
                eval_lst = pickle.load(file)
        else:
            eval_lst = [(0, 0, 0)]

    for i in range(games_num):
        print("Round:", i + 1)
        player1 = create_player(args.player_1, get_heurestic(args.heuristic_1), renderer=renderer, depth=args.depth,
                                load_q_table=args.load_q_table)
        player2 = create_player(args.player_2, get_heurestic(args.heuristic_2), renderer=renderer, depth=args.depth,
                                load_q_table=args.load_q_table)
        game_instance = Dots_and_Boxes(renderer=renderer, games_num=1, number_of_dots=number_of_dots,
                                       player1=player1, player2=player2)
        game_instance.play()

        score1 += game_instance.get_player1_score()
        score2 += game_instance.get_player2_score()
        tie += game_instance.get_tie()

        if isinstance(player1, QLearningAgent):
            result = 'win' if score1 > score2 else 'loss' if score1 < score2 else 'tie'
            player1.reward(player1.round_end_reward(result))
            if args.load_q_table:
                player1.save_q_table()
        if isinstance(player2, QLearningAgent):
            result = 'win' if score2 > score1 else 'loss' if score2 < score1 else 'tie'
            player2.reward(player2.round_end_reward(result))
            if args.load_q_table:
                player2.save_q_table()

        if (i + 1) % 1000 == 0:
            e1 = eval_lst[-1][0]
            e2 = eval_lst[-1][1]
            e3 = eval_lst[-1][2]
            eval_lst.append((score1 - e1, score2 - e2, tie - e3))

        print("---------------------------------------------------------------------------")

    if args.eval:
        with open('eval_data.pkl', 'wb') as file:
            pickle.dump(eval_lst, file)

    print("---------------------------------------------------------------------------")
    print("Final Results:")
    print(f"Player 1 ({args.player_1}): {score1}")
    print(f"Player 2 ({args.player_2}): {score2}")
    print(f"Tie: {tie}")
