import pygame
import numpy as np
import random
import time 
import math

infinity = math.inf

ROWS = 6
COLS = 7

P1_piece = 1
P2_piece = 2

from AI_agent import AI_Agent

class GUI:
    def __init__(self):
        pygame.init()
        self.ai_agent = AI_Agent(ROWS, COLS)
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Connect Four")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.running = True

        self.board_image = pygame.image.load("board.png").convert_alpha()
        self.legend_image = pygame.image.load("legend.png").convert_alpha()
        self.player1_image = pygame.image.load("player1.png").convert_alpha()
        self.player2_image = pygame.image.load("player2.png").convert_alpha()

        self.font = pygame.font.SysFont("Arial", 40)
        self.button_font = pygame.font.SysFont("Arial", 50)

        self.button_rect = pygame.Rect(1100, 650, 300, 100)

        self.reset()

        self.player1_cells = np.array([
            [[117,147],[224,147],[331,147],[438,147],[546,147],[653,147],[761,147]],
            [[117,254],[224,254],[331,254],[438,254],[546,254],[653,254],[761,254]],
            [[117,362],[224,362],[331,362],[438,362],[546,362],[653,362],[761,362]],
            [[117,469],[224,469],[331,469],[438,469],[546,469],[653,469],[761,469]],
            [[117,577],[224,577],[331,577],[438,577],[546,577],[653,577],[761,577]],
            [[117,684],[224,684],[331,684],[438,684],[546,684],[653,684],[761,684]]
        ])

        self.player2_cells = np.array([
            [[118,151],[226,151],[333,151],[440,151],[548,151],[655,151],[763,151]],
            [[118,258],[226,258],[333,258],[440,258],[548,258],[655,258],[763,258]],
            [[118,366],[226,366],[333,366],[440,366],[548,366],[655,366],[763,366]],
            [[118,473],[226,473],[333,473],[440,473],[548,473],[655,473],[763,473]],
            [[118,581],[226,581],[333,581],[440,581],[548,581],[655,581],[763,581]],
            [[118,688],[226,688],[333,688],[440,688],[548,688],[655,688],[763,688]]
        ])

    def reset(self):
        pygame.time.delay(500)
        self.state = np.zeros((6, 7), dtype=int)
        self.current_player = 1
        self.winner = 0

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def animate_piece(self, col, row, player):
        piece_img = self.player1_image if player == 1 else self.player2_image
        final_x, final_y = (self.player1_cells if player == 1 else self.player2_cells)[row, col]
        x = final_x
        y = 10

        while y < final_y:
            y += 30
            self.draw_board()
            self.screen.blit(piece_img, (x, y))
            pygame.display.flip()
            self.clock.tick(60)

    def drop_piece(self, col):
        if self.winner != 0:
            return
        for row in reversed(range(6)):
            if self.state[row, col] == 0:
                self.animate_piece(col, row, self.current_player)
                self.state[row, col] = self.current_player
                self.current_player = 2 if self.current_player == 1 else 1
                return

    def check_winner(self):
        board = self.state
        for row in range(6):
            for col in range(4):
                if board[row, col] != 0 and board[row, col] == board[row, col+1] == board[row, col+2] == board[row, col+3]:
                    return board[row, col]
        for col in range(7):
            for row in range(3):
                if board[row, col] != 0 and board[row, col] == board[row+1, col] == board[row+2, col] == board[row+3, col]:
                    return board[row, col]
        for row in range(3):
            for col in range(4):
                if board[row, col] != 0 and board[row, col] == board[row+1, col+1] == board[row+2, col+2] == board[row+3, col+3]:
                    return board[row, col]
        for row in range(3, 6):
            for col in range(4):
                if board[row, col] != 0 and board[row, col] == board[row-1, col+1] == board[row-2, col+2] == board[row-3, col+3]:
                    return board[row, col]
        if np.all(board != 0):
            return 3
        return 0

    def display_state(self):
        if self.current_player == 1 and self.winner == 0:
            mouse_x, _ = self.get_mouse_position()
            mouse_x -= 50
            cells = self.player1_cells
            column_x_positions = cells[0, :, 0]
            x_snap = min(column_x_positions, key=lambda px: abs(px - mouse_x))
            if mouse_x < 860:
                self.screen.blit(self.player1_image, (x_snap, 10))

        for row in range(6):
            for col in range(7):
                if self.state[row, col] == 1:
                    x, y = self.player1_cells[row, col]
                    self.screen.blit(self.player1_image, (x, y))
                elif self.state[row, col] == 2:
                    x, y = self.player2_cells[row, col]
                    self.screen.blit(self.player2_image, (x, y))

    def ai_move(self):
        col = self.ai_agent.make_move(self.state)
        if col is not None:
            self.drop_piece(col)

    def draw_button(self):
        pygame.draw.rect(self.screen, (0, 150, 255), self.button_rect, border_radius=20)
        text = self.button_font.render("Play Again", True, (255, 255, 255))
        self.screen.blit(text, (self.button_rect.x + 20, self.button_rect.y + 20))

    def draw_winner(self):
        if self.winner == 1:
            msg = "Player 1 Wins"
        elif self.winner == 2:
            msg = "Player 2 Wins"
        elif self.winner == 3:
            msg = "Draw"
        else:
            return
        txt = self.font.render(msg, True, (0, 0, 0))
        self.screen.blit(txt, (1100, 550))

    def draw_board(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.board_image, (100, 125))
        self.screen.blit(self.legend_image, (1100, 125))
        self.display_state()
        self.draw_winner()
        self.draw_button()

    def run(self):
        while self.running:
            if self.current_player == 2 and self.winner == 0:
                self.ai_move()

            for event in pygame.event.get():
                mouse_x, _ = self.get_mouse_position()
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        self.reset()
                    elif self.winner == 0 and self.current_player == 1:
                        column_x_positions = self.player1_cells[0, :, 0]
                        mouse_x -= 50
                        x_snap = min(column_x_positions, key=lambda px: abs(px - mouse_x))
                        col = np.where(column_x_positions == x_snap)[0][0]
                        self.drop_piece(col)

            if self.winner == 0:
                self.winner = self.check_winner()

            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    gui = GUI()
    gui.run()
