import numpy as np

from AI_agent import P1_PIECE, P2_PIECE, EMPTY

P1_PIECE, P2_PIECE, EMPTY = 1, 2, 0
ROWS, COLS = 6, 7

class Heuristic:
    @staticmethod
    def evaluate_window(window, piece):
        score = 0
        opp_piece = P1_PIECE if piece == P2_PIECE else P2_PIECE

        num_piece = window.count(piece)
        num_empty = window.count(EMPTY)
        num_opp = window.count(opp_piece)

        if num_piece == 4: 
            score += 100000
        elif num_piece == 3 and num_empty == 1: 
            score += 50
        elif num_piece == 2 and num_empty == 2: 
            score += 10
        if num_opp == 3 and num_empty == 1: 
            score -= 400
            
        return score

    @staticmethod
    def score_position(board_object, piece):
        """Calculates the total heuristic score for the entire board state."""
        board = board_object.board
        rows = board_object.rows
        cols = board_object.cols
        score = 0

        # 1. Score Center Column preference
        center_array = list(board[:, cols // 2])
        center_count = center_array.count(piece)
        score += center_count * 5

        # 2. Score Horizontal
        for r in range(rows):
            row_array = list(board[r, :])
            for c in range(cols - 3):
                window = row_array[c:c+4]
                score += Heuristic.evaluate_window(window, piece)

        # 3. Score Vertical
        for c in range(cols):
            col_array = list(board[:, c])
            for r in range(rows - 3):
                window = col_array[r:r+4]
                score += Heuristic.evaluate_window(window, piece)

        # 4. Score Positively Sloped Diagonal
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += Heuristic.evaluate_window(window, piece)

        # 5. Score Negatively Sloped Diagonal
        for r in range(3, rows):
            for c in range(cols - 3):
                window = [board[r-i][c+i] for i in range(4)]
                score += Heuristic.evaluate_window(window, piece)

        return score