from players.random_player import RandomPlayer
from dots_and_boxes import Dots_and_Boxes
from Renderers.gui_renderer import GUI_Renderer
from Renderers.console_renderer import ConsoleRenderer
from players.alpha_beta_agent import AlphaBetaPlayer




if __name__ == "__main__":
    number_of_dots = 5
    games_num = 3
    # renderer = GUI_Renderer(number_of_dots, True)
    renderer = ConsoleRenderer(number_of_dots)
    # player1 = HumanPlayer(renderer)
    player1 = RandomPlayer()
    player2 = AlphaBetaPlayer()
    game_instance = Dots_and_Boxes(renderer=renderer,games_num=games_num,number_of_dots=number_of_dots,
                                   player1=player1, player2=player2)
    game_instance.play()
