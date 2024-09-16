from tkinter import *
import numpy as np
from Renderers.renderer import Renderer

class GUI_Renderer(Renderer):
    def __init__(self, number_of_dots=4, show_round_end_screen=False):
        self.window = Tk()
        self.show_round_end_screen = show_round_end_screen
        self.number_of_dots = number_of_dots
        self.window.title('Dots_and_Boxes')
        self.size_of_board = 600
        self.canvas = Canvas(self.window, width=self.size_of_board, height=self.size_of_board)
        self.canvas.pack()
        self.turntext_handle = []
        self.game_start = True
        self.symbol_size = (self.size_of_board / 3 - self.size_of_board / 8) / 2
        self.symbol_thickness = 50
        self.dot_color = '#7BC043'
        self.player1_color = '#0492CF'
        self.player1_color_light = '#67B0CF'
        self.player2_color = '#EE4035'
        self.player2_color_light = '#EE7E77'
        self.Green_color = '#7BC043'
        self.dot_width = 0.25 * self.size_of_board / number_of_dots
        self.edge_width = 0.1 * self.size_of_board / number_of_dots
        self.distance_between_dots = self.size_of_board / (number_of_dots)
        self.LEFT_CLICK = '<Button-1>'

        # Score-related attributes
        self.player1_score = 0
        self.player2_score = 0
        self.score_text_handle = None

    def mainloop(self):
        self.window.mainloop()

    def display_scores(self):
        score_text = f"Player 1: {self.player1_score}  |  Player 2: {self.player2_score}"
        if self.score_text_handle is not None:
            self.canvas.delete(self.score_text_handle)
        self.score_text_handle = self.canvas.create_text(self.size_of_board / 2,
                                                         self.size_of_board - 20,
                                                         font="cmr 11 bold",
                                                         fill="black",
                                                         text=score_text)

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position-self.distance_between_dots/4)//(self.distance_between_dots/2)

        type = False
        logical_position = []
        if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
            x = int((position[0]-1)//2)
            y = int(position[1]//2)
            logical_position = [x, y]
            type = 'row'
        elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
            y = int((position[1] - 1) // 2)
            x = int(position[0] // 2)
            logical_position = [x, y]
            type = 'col'

        return type, logical_position


    def shade_box(self, box, player):
        color = self.player1_color_light if player == 1 else self.player2_color_light
        start_x = self.distance_between_dots / 2 + box[1] * self.distance_between_dots + self.edge_width/2
        start_y = self.distance_between_dots / 2 + box[0] * self.distance_between_dots + self.edge_width/2
        end_x = start_x + self.distance_between_dots - self.edge_width
        end_y = start_y + self.distance_between_dots - self.edge_width
        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill=color, outline='')

        # Update the score based on the player who completed the box
        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1
        self.display_scores()

    def make_edge(self, type, logical_position, player_turn):
        if self.game_start:
            self.canvas.delete("all")
            self.game_start = False

        if type == 'row':
            start_x = self.distance_between_dots/2 + logical_position[0]*self.distance_between_dots
            end_x = start_x+self.distance_between_dots
            start_y = self.distance_between_dots/2 + logical_position[1]*self.distance_between_dots
            end_y = start_y
        elif type == 'col':
            start_y = self.distance_between_dots / 2 + logical_position[1] * self.distance_between_dots
            end_y = start_y + self.distance_between_dots
            start_x = self.distance_between_dots / 2 + logical_position[0] * self.distance_between_dots
            end_x = start_x

        if player_turn == 1:
            color = self.player1_color
        else:
            color = self.player2_color
        self.canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=self.edge_width)

    def display_gameover(self, player1_score, player2_score):

        if player1_score > player2_score:
            text = 'Winner: Player 1 '
            color = self.player1_color
        elif player2_score > player1_score:
            text = 'Winner: Player 2 '
            color = self.player2_color
        else:
            text = 'Its a tie'
            color = 'gray'
        self.window.quit()

        self.canvas.delete("all")
        self.canvas.create_text(self.size_of_board / 2, self.size_of_board / 3, font="cmr 60 bold", fill=color, text=text)

        score_text = 'Scores \n'
        self.canvas.create_text(self.size_of_board / 2, 5 * self.size_of_board / 8, font="cmr 40 bold", fill=self.Green_color,
                                text=score_text)

        score_text = 'Player 1 : ' + str(player1_score) + '\n'
        score_text += 'Player 2 : ' + str(player2_score) + '\n'
        self.canvas.create_text(self.size_of_board / 2, 3 * self.size_of_board / 4, font="cmr 30 bold", fill=self.Green_color,
                                text=score_text)


    def refresh_board(self):
        for i in range(self.number_of_dots):
            x = i * self.distance_between_dots + self.distance_between_dots / 2
            self.canvas.create_line(x, self.distance_between_dots / 2, x,
                                    self.size_of_board - self.distance_between_dots / 2,
                                    fill='gray', dash=(2, 2))
            self.canvas.create_line(self.distance_between_dots / 2, x,
                                    self.size_of_board - self.distance_between_dots / 2, x,
                                    fill='gray', dash=(2, 2))

        for i in range(self.number_of_dots):
            for j in range(self.number_of_dots):
                start_x = i * self.distance_between_dots + self.distance_between_dots / 2
                end_x = j * self.distance_between_dots + self.distance_between_dots / 2
                self.canvas.create_oval(start_x - self.dot_width / 2, end_x - self.dot_width / 2, start_x + self.dot_width / 2,
                                        end_x + self.dot_width / 2, fill=self.dot_color,
                                        outline=self.dot_color)


    def display_turn_text(self, player):
        text = 'Next turn: '
        if player==1:
            text += 'Player1'
            color = self.player1_color
        else:
            text += 'Player2'
            color = self.player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(self.size_of_board - 5*len(text),
                                                       self.size_of_board-self.distance_between_dots/8,
                                                       font="cmr 15 bold", text=text, fill=color)
    def restart_game(self, player1_score, player2_score):
        self.window.unbind(self.LEFT_CLICK)
        self.canvas.delete("all")
        if self.show_round_end_screen:
            self.display_gameover(player1_score, player2_score)
        self.window.quit()
        # self.refresh_board()
        # self.game_start=True

    def display_final_score(self, winner_scores):
        self.canvas.delete("all")
        score_text = 'Scores \n'
        for key, val in winner_scores.items():
            score_text += f'{key}: {val}\n''\n'
        self.canvas.create_text(self.size_of_board / 2, 3 * self.size_of_board / 4, font="cmr 40 bold", fill=self.Green_color,
                                text=score_text)

    def window_scheduler(self,player_wait_time,player_turn, current_player):
        self.window.after(player_wait_time, player_turn, current_player)

    def window_bind(self,click):
        self.window.bind(self.LEFT_CLICK, click)