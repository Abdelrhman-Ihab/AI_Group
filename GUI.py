import pygame
import numpy as np

from AI_agent import AI_Agent, ConnectFourBoard, ROWS, COLS, P1_PIECE, P2_PIECE, INF 

class GUI:
    def __init__(self):
        pygame.init()
        self.W, self.H = 1600, 900
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Connect Four AI")

        # Load resources (with fallbacks)
        try:
            self.board_image = pygame.image.load("board.png").convert_alpha()
            self.legend_image = pygame.image.load("legend.png").convert_alpha()
            self.player1_image = pygame.image.load("player1.png").convert_alpha()
            self.player2_image = pygame.image.load("player2.png").convert_alpha()
        except pygame.error:
            # Simple circle fallbacks if images are missing
            print("Warning: Missing image files. Using colored circles as fallback.")
            self.board_image = pygame.Surface((700, 600)); self.board_image.fill((0, 0, 255))
            self.legend_image = pygame.Surface((300, 500)); self.legend_image.fill((200, 200, 200))
            self.player1_image = pygame.Surface((100, 100), pygame.SRCALPHA); pygame.draw.circle(self.player1_image, (255, 0, 0), (50, 50), 45)
            self.player2_image = pygame.Surface((100, 100), pygame.SRCALPHA); pygame.draw.circle(self.player2_image, (255, 255, 0), (50, 50), 45)

        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 40)
        self.button_font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)

        self.game_state = 'CONFIG'
        self.depth_k = 5
        self.algo_choice = 2
        self.ai_agent = None
        self.winner = 0
        self.final_score_msg = ""

        self.button_rect = pygame.Rect(1200, 650, 300, 100)
        self.init_config_rects()
        self.load_piece_coordinates()
        self.reset_game_state()

    def load_piece_coordinates(self):
        """Pre-defined cell coordinates from the original GUI code."""
        # Maps the 6x7 board visually. Visual Row 5 (index 5) is the bottom row.
        self.player1_cells = np.array([
            [[117,147],[224,147],[331,147],[438,147],[546,147],[653,147],[761,147]], # Visual Row 0 (TOP)
            [[117,254],[224,254],[331,254],[438,254],[546,254],[653,254],[761,254]],
            [[117,362],[224,362],[331,362],[438,362],[546,362],[653,362],[761,362]],
            [[117,469],[224,469],[331,469],[438,469],[546,469],[653,469],[761,469]],
            [[117,577],[224,577],[331,577],[438,577],[546,577],[653,577],[761,577]],
            [[117,684],[224,684],[331,684],[438,684],[546,684],[653,684],[761,684]]  # Visual Row 5 (BOTTOM)
        ])
        self.player2_cells = self.player1_cells # Use same coords for simplicity in this implementation

    def init_config_rects(self):
        """Initializes rects for configuration screen buttons."""
        center_x = self.W // 2
        self.algo_rects = {
            1: pygame.Rect(center_x - 450, 450, 280, 50),
            2: pygame.Rect(center_x - 140, 450, 280, 50),
            3: pygame.Rect(center_x + 170, 450, 280, 50),
        }
        self.k_minus_rect = pygame.Rect(center_x - 100, 320, 50, 50)
        self.k_plus_rect = pygame.Rect(center_x + 50, 320, 50, 50)
        self.start_button_rect = pygame.Rect(center_x - 150, 600, 300, 70)

    def reset_game_state(self):
        """Resets the board state for a new game."""
        self.state = np.zeros((ROWS, COLS), dtype=int)
        self.current_player = P1_PIECE
        self.winner = 0
        self.final_score_msg = ""
        # AI_Agent is only initialized/re-initialized upon starting from the config screen

    def reset_to_config(self):
        """Resets all states and goes back to the configuration screen."""
        self.game_state = 'CONFIG'
        self.winner = 0
        self.ai_agent = None

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def animate_piece(self, col, row, player):
        """Animates a piece dropping into the board."""
        piece_img = self.player1_image if player == P1_PIECE else self.player2_image
        
        # Map the logical row (r=0 is bottom) to the visual cell array index (visual_r=5 is bottom)
        visual_r = ROWS - 1 - row 
        final_x, final_y = self.player1_cells[visual_r, col]
        
        x = final_x
        y = 10 

        while y < final_y:
            y += 30
            self.draw_board() 
            self.screen.blit(piece_img, (x, y))
            pygame.display.flip()
            self.clock.tick(60)

    def drop_piece(self, col):
        """Drops a piece, updates state, and switches player."""
        if self.winner != 0: return

        # Use ConnectFourBoard utility from ai_agent module
        board_obj = ConnectFourBoard(ROWS, COLS, self.state) 
        land_row = board_obj.get_next_open_row(col)

        if land_row != -1:
            self.animate_piece(col, land_row, self.current_player)
            self.state[land_row, col] = self.current_player
            self.current_player = P2_PIECE if self.current_player == P1_PIECE else P1_PIECE

    def check_winner(self):
        """Game termination check: returns 3 ONLY when the board is full (Required Rule)."""
        board_obj = ConnectFourBoard(ROWS, COLS, self.state)
        if len(board_obj.get_valid_moves()) == 0:
            return 3 # Board Full -> Game Over

        return 0 # Continue playing

    def ai_move(self):
        """Gets the move from the AI agent and drops the piece."""
        col = self.ai_agent.make_move(self.state)
        if col is not None:
            self.drop_piece(col)

    # --- Drawing Functions ---

    def draw_button(self, rect, text, is_active=False):
        """Helper to draw a button."""
        color = (0, 150, 255) if not is_active else (50, 200, 100)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        if is_active:
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 4, border_radius=10)

        text_surf = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_config_screen(self):
        """Draws the screen for selecting K and Algorithm."""
        self.screen.fill((240, 240, 240))
        center_x = self.W // 2
        title_text = self.title_font.render("Connect Four AI Configuration", True, (50, 50, 50))
        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, 100))
        k_label = self.font.render("Select Search Depth K:", True, (50, 50, 50))
        self.screen.blit(k_label, (center_x - k_label.get_width() // 2, 250))
        k_value_text = self.font.render(str(self.depth_k), True, (0, 0, 0))
        k_value_rect = k_value_text.get_rect(center=(center_x, 345))
        pygame.draw.rect(self.screen, (255, 255, 255), k_value_rect.inflate(10, 10), border_radius=5)
        self.screen.blit(k_value_text, k_value_rect)
        self.draw_button(self.k_minus_rect, "-", is_active=False)
        self.draw_button(self.k_plus_rect, "+", is_active=False)
        algo_label = self.font.render("Select AI Algorithm:", True, (50, 50, 50))
        self.screen.blit(algo_label, (center_x - algo_label.get_width() // 2, 400))
        self.draw_button(self.algo_rects[1], "1. Minimax (No AB)", is_active=(self.algo_choice == 1))
        self.draw_button(self.algo_rects[2], "2. Minimax (With AB)", is_active=(self.algo_choice == 2))
        self.draw_button(self.algo_rects[3], "3. Expected Minimax", is_active=(self.algo_choice == 3))
        self.draw_button(self.start_button_rect, "START GAME", is_active=False)


    def draw_board(self):
        """Draws the main game board and game-specific elements."""
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.board_image, (100, 125))
        self.screen.blit(self.legend_image, (1100, 125))
        self.display_state()
        if self.winner != 0:
            self.draw_winner()
        else:
            player_msg = f"Current Turn: Player {self.current_player} ({'Human' if self.current_player == P1_PIECE else 'AI'})"
            txt = self.font.render(player_msg, True, (0, 0, 0))
            self.screen.blit(txt, (1100, 550))
        self.draw_button(self.button_rect, "Play Again", is_active=False)

    def display_state(self):
        """Draws the current board pieces and the next player's dropping piece."""
        # Floating piece logic (Human)
        if self.current_player == P1_PIECE and self.winner == 0:
            mouse_x, _ = self.get_mouse_position()
            column_x_positions = self.player1_cells[0, :, 0]
            mouse_x_for_snap = mouse_x - 50
            x_snap = min(column_x_positions, key=lambda px: abs(px - mouse_x_for_snap))
            if mouse_x > 100 and mouse_x < 900:
                self.screen.blit(self.player1_image, (x_snap, 10))

        # Draw all pieces on the board
        for r in range(ROWS):
            for c in range(COLS):
                # Map the logical row (r=0 is bottom) to the visual index (visual_r=5 is bottom)
                visual_r = ROWS - 1 - r 
                
                if self.state[r, c] == P1_PIECE:
                    x, y = self.player1_cells[visual_r, c] 
                    self.screen.blit(self.player1_image, (x, y))
                elif self.state[r, c] == P2_PIECE:
                    x, y = self.player2_cells[visual_r, c]
                    self.screen.blit(self.player2_image, (x, y))

    def draw_winner(self):
        """Displays the winner message (only board full scoring remains)."""
        msg = ""
        
        if self.winner == 3:
            if not self.final_score_msg:
                self.final_score_msg = self.calculate_final_score()
            msg = self.final_score_msg

        txt = self.font.render(msg, True, (0, 0, 0))
        self.screen.blit(txt, (1100, 550))


    def calculate_final_score(self):
        """Calculates final winner based on connected 4s when board is full."""
        board_obj = ConnectFourBoard(ROWS, COLS, self.state)
        human_fours = board_obj.count_all_fours(P1_PIECE)
        ai_fours = board_obj.count_all_fours(P2_PIECE)

        if ai_fours > human_fours:
            return f"AI WINS! (AI: {ai_fours} Fours vs Human: {human_fours} Fours)"
        elif human_fours > ai_fours:
            return f"HUMAN WINS! (Human: {human_fours} Fours vs AI: {ai_fours} Fours)"
        else:
            return f"IT'S A DRAW! (Both: {human_fours} Fours)"


    # --- Event Handling ---

    def handle_config_events(self, event):
        """Handles events specific to the configuration screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.k_minus_rect.collidepoint(pos) and self.depth_k > 1: self.depth_k -= 1
            elif self.k_plus_rect.collidepoint(pos) and self.depth_k < 10: self.depth_k += 1
            for choice, rect in self.algo_rects.items():
                if rect.collidepoint(pos): self.algo_choice = choice
            if self.start_button_rect.collidepoint(pos):
                self.ai_agent = AI_Agent(ROWS, COLS, self.depth_k, self.algo_choice)
                self.game_state = 'PLAYING'
                self.reset_game_state()

    def handle_playing_events(self, event):
        """Handles events specific to the playing screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.button_rect.collidepoint(pos):
                self.reset_to_config()
                return

            if self.winner == 0 and self.current_player == P1_PIECE:
                mouse_x, _ = self.get_mouse_position()
                column_x_positions = self.player1_cells[0, :, 0]
                mouse_x_for_snap = mouse_x - 50

                if mouse_x > 100 and mouse_x < 900:
                    x_snap = min(column_x_positions, key=lambda px: abs(px - mouse_x_for_snap))
                    col = np.where(column_x_positions == x_snap)[0][0]
                    
                    board_obj = ConnectFourBoard(ROWS, COLS, self.state)
                    if board_obj.is_valid_location(col):
                        self.drop_piece(col)

    def run(self):
        """Main game loop."""
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                
                if self.game_state == 'CONFIG':
                    self.handle_config_events(event)
                else:
                    self.handle_playing_events(event)

            if self.game_state == 'CONFIG':
                self.draw_config_screen()
            else:
                # AI's Turn
                if self.game_state == 'PLAYING' and self.current_player == P2_PIECE:
                    self.ai_move()
                
                # Check for board full after any move
                if self.winner == 0:
                    self.winner = self.check_winner()

                if self.winner != 0:
                    self.game_state = 'GAME_OVER'

                self.draw_board()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    gui = GUI()
    gui.run()