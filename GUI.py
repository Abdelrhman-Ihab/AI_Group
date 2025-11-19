import random
import pygame
import numpy as np
from AI_agent import AI_Agent
PROB_CHOSEN = 0.6
PROB_SIDE_AVAILABLE = 0.2
PROB_ONE_SIDE_ONLY = 0.4
ROWS = 6
COLS = 7


def is_valid_location(col,board):
    return board[ROWS - 1][col] == 0# empty

def stochastic_drop_column(chosen_col, board):
    """
    Returns the column where the disc actually falls based on probabilities.
    board: np.array
    """
    left_col = chosen_col - 1
    right_col = chosen_col + 1

    outcomes = []
    # Check which neighboring columns are valid
    valid_left = left_col >= 0 and is_valid_location(left_col, board)
    valid_right = right_col < COLS and is_valid_location(right_col, board)
    
    if valid_left and valid_right:
        outcomes = [(chosen_col, 0.6), (left_col, 0.2), (right_col, 0.2)]
    elif valid_left:
        outcomes = [(chosen_col, 0.6), (left_col, 0.4)]
    elif valid_right:
        outcomes = [(chosen_col, 0.6), (right_col, 0.4)]
    else:
        outcomes = [(chosen_col, 1.0)]

    # Choose column based on probabilities
    cols, probs = zip(*outcomes)
    actual_col = random.choices(cols, weights=probs, k=1)[0]
    return actual_col


# ----------------- Menu Class -----------------
class Menu:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Connect Four - Menu")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 60)
        self.button_font = pygame.font.SysFont("Arial", 50)
        self.running = True

        self.depth = 4
        self.algorithm = "Minimax"
        
        # --- DYNAMICALLY CENTERED LAYOUT COORDINATES ---
        
        X_CENTER = self.width // 2
        
        # Total Menu Block Vertical Extent (Approximate height from Title top to Start bottom is 490px)
        BLOCK_HEIGHT = 490 
        # Calculate the Y coordinate for the top of the entire menu block to center it vertically
        Y_BLOCK_TOP = self.height // 2 - BLOCK_HEIGHT // 2 
        
        # 1. Algorithm buttons block (Total width: 740px: 3*220 + 2*40)
        BLOCK_WIDTH_ALGO = 740
        X_START_ALGO = X_CENTER - BLOCK_WIDTH_ALGO // 2
        Y_ALGO = Y_BLOCK_TOP + 110 # 110px offset from the block top
        
        self.minimax_btn = pygame.Rect(X_START_ALGO, Y_ALGO, 220, 60)
        self.alpha_btn = pygame.Rect(X_START_ALGO + 260, Y_ALGO, 220, 60)
        self.expected_btn = pygame.Rect(X_START_ALGO + 520, Y_ALGO, 220, 60)

        # 2. Depth controls block (Total width: 220px: 2*100 + 1*20)
        BLOCK_WIDTH_DEPTH = 220
        X_START_DEPTH = X_CENTER - BLOCK_WIDTH_DEPTH // 2
        Y_DEPTH_BUTTONS = Y_BLOCK_TOP + 300 # 300px offset from the block top
        
        self.depth_up = pygame.Rect(X_START_DEPTH, Y_DEPTH_BUTTONS, 100, 60) 
        self.depth_down = pygame.Rect(X_START_DEPTH + 120, Y_DEPTH_BUTTONS, 100, 60)
        
        # 3. Start button (200px wide)
        X_START_BUTTON = X_CENTER - 200 // 2
        Y_START_BUTTON = Y_BLOCK_TOP + 410 # 410px offset from the block top
        self.start_btn = pygame.Rect(X_START_BUTTON, Y_START_BUTTON, 200, 80)

        # Store Y_BLOCK_TOP for use in draw method
        self.y_block_top = Y_BLOCK_TOP

    def draw(self):
        # Background: White
        self.screen.fill((255, 255, 255))

        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        BLUE_BTN = (0, 150, 255)
        SELECTED_BLUE = (0, 150, 255)
        UNSELECTED_BLUE = (0, 70, 150)

        # --- Title (Perfectly Centered) ---
        title_text = self.font.render("Connect Four AI", True, BLACK)
        # Y is calculated based on the centered block top + half the title height
        title_rect = title_text.get_rect(center=(self.width // 2, self.y_block_top + 30))
        self.screen.blit(title_text, title_rect)

        # --- Algorithm selection (Horizontal, Centered Block) ---
        pygame.draw.rect(self.screen, SELECTED_BLUE if self.algorithm=="Minimax" else UNSELECTED_BLUE, self.minimax_btn, border_radius=10)
        pygame.draw.rect(self.screen, SELECTED_BLUE if self.algorithm=="Alpha-Beta" else UNSELECTED_BLUE, self.alpha_btn, border_radius=10)
        pygame.draw.rect(self.screen, SELECTED_BLUE if self.algorithm=="Expected" else UNSELECTED_BLUE, self.expected_btn, border_radius=10)
        
        # Center algorithm text using button.center
        minimax_text = self.button_font.render("Minimax", True, WHITE)
        minimax_rect = minimax_text.get_rect(center=self.minimax_btn.center)
        self.screen.blit(minimax_text, minimax_rect)
        
        alpha_text = self.button_font.render("Alpha-Beta", True, WHITE)
        alpha_rect = alpha_text.get_rect(center=self.alpha_btn.center)
        self.screen.blit(alpha_text, alpha_rect)
        
        expected_text = self.button_font.render("Expected", True, WHITE)
        expected_rect = expected_text.get_rect(center=self.expected_btn.center)
        self.screen.blit(expected_text, expected_rect)


        # --- Depth selector (Centralized Block) ---
        # Depth Label and Value (Grouped and Centered)
        depth_label_value = self.font.render(f"Depth: {self.depth}", True, BLACK)
        # Y is calculated based on the centered block top + center Y of the label
        depth_label_value_rect = depth_label_value.get_rect(center=(self.width // 2, self.y_block_top + 250))
        self.screen.blit(depth_label_value, depth_label_value_rect)

        # Draw depth buttons with border_radius
        pygame.draw.rect(self.screen, BLUE_BTN, self.depth_up, border_radius=10)
        pygame.draw.rect(self.screen, BLUE_BTN, self.depth_down, border_radius=10)

        # Center + and - text
        plus_text = self.font.render("+", True, BLACK)
        plus_rect = plus_text.get_rect(center=self.depth_up.center)
        self.screen.blit(plus_text, plus_rect)

        minus_text = self.font.render("-", True, BLACK)
        minus_rect = minus_text.get_rect(center=self.depth_down.center)
        self.screen.blit(minus_text, minus_rect)


        # Start button (Centered)
        pygame.draw.rect(self.screen, BLUE_BTN, self.start_btn, border_radius=15)
        start_text = self.button_font.render("Start", True, WHITE)
        start_rect = start_text.get_rect(center=self.start_btn.center)
        self.screen.blit(start_text, start_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None, None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None, None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if self.depth_up.collidepoint(mx, my):
                        self.depth = min(20, self.depth + 1)
                    if self.depth_down.collidepoint(mx, my):
                        self.depth = max(1, self.depth - 1)
                    if self.minimax_btn.collidepoint(mx, my):
                        self.algorithm = "Minimax"
                    if self.alpha_btn.collidepoint(mx, my):
                        self.algorithm = "Alpha-Beta"
                    global expected_flag
                    if self.expected_btn.collidepoint(mx, my):
                        self.algorithm = "Expected"
                        expected_flag = True
                        
                    if self.start_btn.collidepoint(mx, my):
                        self.running = False
                        return self.depth, self.algorithm
            self.clock.tick(60)
        return None, None
# ----------------- GUI Class -----------------
class GUI:
    def __init__(self):
        # --- Show Menu first ---
        menu = Menu()
        depth, algorithm = menu.run()
        if depth is None:
            pygame.quit()
            exit()

        self.ai_agent = AI_Agent(depth= depth, algorithm = algorithm)

        # --- Initialize game ---
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Connect Four")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.running = True

        # Images
        self.board_image = pygame.image.load("board.png").convert_alpha()
        self.legend_image = pygame.image.load("legend.png").convert_alpha()
        self.player1_image = pygame.image.load("player1.png").convert_alpha()
        self.player2_image = pygame.image.load("player2.png").convert_alpha()

        # Fonts & button
        self.font = pygame.font.SysFont("Arial", 40)
        self.button_font = pygame.font.SysFont("Arial", 50)
        self.button_rect = pygame.Rect(1100, 650, 300, 100)

        # Board
        self.reset()

        # Piece positions
        self.player1_cells = np.array([
            [[117,147],[224,147],[331,147],[438,147],[546,147],[653,147],[761,147]],
            [[117,254],[224,254],[331,254],[438,254],[546,254],[653,254],[761,254]],
            [[117,362],[224,362],[331,362],[438,362],[546,362],[653,362],[761,362]],
            [[117,469],[224,469],[331,469],[438,469],[546,469],[653,469],[761,469]],
            [[117,577],[224,577],[331,577],[438,577],[546,577],[653,577],[761,577]],
            [[117,684],[224,684],[331,684],[438,684],[546,684],[653,684],[761,684]]
        ])
        self.player2_cells = self.player1_cells + 1

    def reset(self):
        pygame.time.delay(500)
        self.state = np.zeros((6,7),dtype=int)
        self.current_player = 1
        self.winner = 0

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def animate_piece(self, col, row, player):
        piece_img = self.player1_image if player==1 else self.player2_image
        final_x, final_y = (self.player1_cells if player==1 else self.player2_cells)[row,col]
        x = final_x
        y = 10
        while y < final_y:
            y += 30
            self.draw_board()
            self.screen.blit(piece_img, (x,y))
            pygame.display.flip()
            self.clock.tick(60)

    def drop_piece(self,col):
        global expected_flag
        if self.winner!=0: return
        if expected_flag :
            col = stochastic_drop_column(col,self.state)
        for row in reversed(range(6)):
            if self.state[row,col]==0:
                self.animate_piece(col,row,self.current_player)
                self.state[row,col]=self.current_player
                self.current_player=2 if self.current_player==1 else 1
                return

    def count_fours(self):
        board = self.state
        p1=p2=0
        # horizontal
        for row in range(6):
            for col in range(4):
                line=board[row,col:col+4]
                if np.all(line==1): p1+=1
                elif np.all(line==2): p2+=1
        # vertical
        for col in range(7):
            for row in range(3):
                line=board[row:row+4,col]
                if np.all(line==1): p1+=1
                elif np.all(line==2): p2+=1
        # diag down-right
        for row in range(3):
            for col in range(4):
                line=[board[row+i,col+i] for i in range(4)]
                if all(x==1 for x in line): p1+=1
                elif all(x==2 for x in line): p2+=1
        # diag up-right
        for row in range(3,6):
            for col in range(4):
                line=[board[row-i,col+i] for i in range(4)]
                if all(x==1 for x in line): p1+=1
                elif all(x==2 for x in line): p2+=1
        return p1,p2

    def check_winner(self):
        if np.all(self.state!=0):
            p1,p2=self.count_fours()
            if p1>p2: return 1
            elif p2>p1: return 2
            else: return 3
        return 0

    def display_state(self):
        for row in range(6):
            for col in range(7):
                if self.state[row,col]==1:
                    x,y=self.player1_cells[row,col]
                    self.screen.blit(self.player1_image,(x,y))
                elif self.state[row,col]==2:
                    x,y=self.player2_cells[row,col]
                    self.screen.blit(self.player2_image,(x,y))
        # hover piece
        if self.current_player == 1 and self.winner == 0:
            mouse_x, _ = self.get_mouse_position()
            col_x = self.player1_cells[0, :, 0]  # shape (7,)
            diffs = np.abs(col_x - mouse_x)
            col_idx = int(np.argmin(diffs))  # closest column index
            x_snap = col_x[col_idx]          # the x coordinate for that column
            if mouse_x < 860:
                self.screen.blit(self.player1_image, (x_snap, 10))

    def ai_move(self):
        col=self.ai_agent.make_move(self.state)
        if col is not None:
            self.drop_piece(col)
            
    
    def draw_button(self):
        pygame.draw.rect(self.screen,(0,150,255),self.button_rect,border_radius=20)
        text=self.button_font.render("Play Again",True,(255,255,255))
        self.screen.blit(text,(self.button_rect.x+20,self.button_rect.y+20))

    def draw_winner(self):
        if self.winner==1: msg="Player 1 Wins"
        elif self.winner==2: msg="Player 2 Wins"
        elif self.winner==3: msg="Draw"
        else: return
        txt=self.font.render(msg,True,(0,0,0))
        self.screen.blit(txt,(1100,550))

    def draw_board(self):
        self.screen.fill((255,255,255))
        self.screen.blit(self.board_image,(100,125))
        self.screen.blit(self.legend_image,(1100,125))
        self.display_state()
        self.draw_winner()
        self.draw_button()

    def run(self):
        while self.running:
            # AI move
            if self.current_player == 2 and self.winner == 0:
                self.ai_move()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos  # <-- unpack tuple correctly

                    # Reset button
                    if self.button_rect.collidepoint(mx, my):
                        self.reset()

                    # Player move
                    elif self.winner == 0 and self.current_player == 1:
                        # Get top row x coordinates
                        col_x = self.player1_cells[0, :, 0]  # shape (7,)
                        # Snap mouse x to closest column
                        mouse_x = int(mx - 50)  # ensure integer
                        col_idx = int(np.argmin(np.abs(col_x - mouse_x)))
                        # Drop piece in selected column
                        self.drop_piece(col_idx)

            # Check winner
            if self.winner == 0:
                self.winner = self.check_winner()

            # Draw everything
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ----------------- Run Game -----------------
if __name__=="__main__":
    gui=GUI()
    gui.run()
