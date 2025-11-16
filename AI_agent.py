import random
import numpy as np

class AI_Agent:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype = int)
        
    def is_valid_location(self, col):
        return self.board[self.rows - 1][col] == 0
    
    def get_next_empty_row(self, col):
        for r in range(self.rows):
            if self.board[r][col] == 0:
                return r
    
    def insert_piece(self, row, col, piece):
        self.board[row][col] = piece
            
    def get_valid_moves(self):
        valid_moves = []
        for col in range(self.cols):
            if self.is_valid_location(col):
                valid_moves.append(col)
        return valid_moves
    
    def count_all_fours(self, piece):
        count = 0
        
    def is_game_over(self):
        return len(self.get_valid_moves()) == 0
         
    def make_move(self, state : np.array):
        valid_cols = [c for c in range(state.shape[1]) if state[0, c] == 0]
        if not valid_cols:
            return None
        col = random.choice(valid_cols)
        return col