import numpy as np
import random
import time
import math
from heuristic import Heuristic 


infinity = math.inf
INF = math.inf
ROWS = 6
COLS = 7
EMPTY = 0
P1_PIECE = 1  # (Human)
P2_PIECE = 2  #(AI)

PROB_CHOSEN = 0.6
PROB_SIDE_AVAILABLE = 0.2
PROB_ONE_SIDE_ONLY = 0.4

# Global counter for nodes expanded in Minimax
nodes_expanded = 0

class ConnectFourBoard:
    def __init__(self, rows=ROWS, cols=COLS, initial_board=None):
        self.rows = rows
        self.cols = cols
        if initial_board is not None:
            self.board = initial_board
        else:
            # Logical row 0 is the bottom-most row
            self.board = np.zeros((rows, cols), dtype=int)

    def is_valid_location(self, col):
        return self.board[self.rows - 1][col] == EMPTY

    def get_next_open_row(self, col):
        for r in range(self.rows):
            if self.board[r][col] == EMPTY:
                return r
        return -1

    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def get_valid_moves(self):
        valid_moves = []
        for col in range(self.cols):
            if self.is_valid_location(col):
                valid_moves.append(col)
        return valid_moves

    def count_all_fours(self, piece):
        count = 0
        # Check Horizontal, Vertical, and both Diagonals
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if all(self.board[r][c+i] == piece for i in range(4)): count += 1 # Horizontal

        for c in range(self.cols):
            for r in range(self.rows - 3):
                if all(self.board[r+i][c] == piece for i in range(4)): count += 1 # Vertical

        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if all(self.board[r+i][c+i] == piece for i in range(4)): count += 1 # Positive Diagonal

        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if all(self.board[r-i][c+i] == piece for i in range(4)): count += 1 # Negative Diagonal

        return count

    def check_win(self, piece):
        return self.count_all_fours(piece) > 0

    def is_terminal_node(self):
        return len(self.get_valid_moves()) == 0

def minimax(board_object, depth, alpha, beta, maximizing_player, heuristic_func, use_alpha_beta):
    global nodes_expanded
    nodes_expanded += 1

    is_board_full = board_object.is_terminal_node() 

    if depth == 0 or is_board_full:
        return (None, heuristic_func(board_object, P2_PIECE)) 

    valid_moves = board_object.get_valid_moves()
    best_col = random.choice(valid_moves)

    if maximizing_player:
        value = -INF
        for col in valid_moves:
            temp_board_obj = ConnectFourBoard(ROWS, COLS, board_object.board.copy()) 
            row = temp_board_obj.get_next_open_row(col)
            temp_board_obj.drop_piece(row, col, P2_PIECE)
            new_score = minimax(temp_board_obj, depth - 1, alpha, beta, False, heuristic_func, use_alpha_beta)[1]

            if new_score > value:
                value = new_score
                best_col = col

            if use_alpha_beta:
                alpha = max(alpha, value)
                if alpha >= beta: break
        return best_col, value
    else:
        value = INF
        for col in valid_moves:
            temp_board_obj = ConnectFourBoard(ROWS, COLS, board_object.board.copy())
            row = temp_board_obj.get_next_open_row(col)
            temp_board_obj.drop_piece(row, col, P1_PIECE)
            new_score = minimax(temp_board_obj, depth - 1, alpha, beta, True, heuristic_func, use_alpha_beta)[1]

            if new_score < value:
                value = new_score
                best_col = col

            if use_alpha_beta:
                beta = min(beta, value)
                if alpha >= beta: break
        return best_col, value

def chance_node(board_object, chosen_col, depth, next_is_max, heuristic_func):
    """Calculates the expected value of a move based on probabilistic outcomes."""
    global nodes_expanded
    nodes_expanded += 1
    total_expected_value = 0
    outcomes = []
    left_col, right_col = chosen_col - 1, chosen_col + 1
    is_left_available = left_col >= 0 and board_object.is_valid_location(left_col)
    is_right_available = right_col < COLS and board_object.is_valid_location(right_col)

    if is_left_available and is_right_available:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((left_col, PROB_SIDE_AVAILABLE))
        outcomes.append((right_col, PROB_SIDE_AVAILABLE))
    elif is_left_available:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((left_col, PROB_ONE_SIDE_ONLY))
    elif is_right_available:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((right_col, PROB_ONE_SIDE_ONLY))
    else:
        outcomes.append((chosen_col, 1.0))

    for col, prob in outcomes:
        if board_object.is_valid_location(col):
            temp_board_obj = ConnectFourBoard(ROWS, COLS, board_object.board.copy())
            row = temp_board_obj.get_next_open_row(col)
            temp_board_obj.drop_piece(row, col, P2_PIECE)
            score_of_outcome = expected_minimax(temp_board_obj, depth - 1, next_is_max, heuristic_func)[1]
            total_expected_value += (score_of_outcome * prob)
    return total_expected_value

def expected_minimax(board_object, depth, maximizing_player, heuristic_func):
    """Expected Minimax algorithm."""
    global nodes_expanded
    nodes_expanded += 1

    is_board_full = board_object.is_terminal_node()

    if depth == 0 or is_board_full:
        return (None, heuristic_func(board_object, P2_PIECE))

    valid_moves = board_object.get_valid_moves()
    best_col = random.choice(valid_moves)

    if maximizing_player:
        value = -INF
        for col in valid_moves:
            expected_score = chance_node(board_object, col, depth, False, heuristic_func)
            if expected_score > value:
                value = expected_score
                best_col = col
        return best_col, value
    else:
        value = INF
        for col in valid_moves:
            temp_board_obj = ConnectFourBoard(ROWS, COLS, board_object.board.copy())
            row = temp_board_obj.get_next_open_row(col)
            temp_board_obj.drop_piece(row, col, P1_PIECE)
            new_score = expected_minimax(temp_board_obj, depth - 1, True, heuristic_func)[1]
            if new_score < value:
                value = new_score
                best_col = col
        return best_col, value


class AI_Agent:
    def __init__(self, rows, cols, depth, algorithm_choice):
        self.rows = rows
        self.cols = cols
        self.K = depth
        self.algorithm_choice = algorithm_choice
        self.heuristic_func = Heuristic.score_position

    def make_move(self, current_board_array):
        global nodes_expanded
        nodes_expanded = 0

        board_obj = ConnectFourBoard(self.rows, self.cols, current_board_array.copy())
        if not board_obj.get_valid_moves():
            return None

        start_time = time.time()
        
        # Select and run the chosen algorithm
        if self.algorithm_choice == 1:
            col, score = minimax(board_obj, self.K, -INF, INF, True, self.heuristic_func, False)
            algorithm_name = "Minimax (No Alpha-Beta)"
        elif self.algorithm_choice == 2:
            col, score = minimax(board_obj, self.K, -INF, INF, True, self.heuristic_func, True)
            algorithm_name = "Minimax (With Alpha-Beta)"
        elif self.algorithm_choice == 3:
            col, score = expected_minimax(board_obj, self.K, True, self.heuristic_func)
            algorithm_name = "Expected Minimax"
        else:
            return None

        end_time = time.time()

        # Output trace information to the console
        print("\n" + "="*50)
        print(f"AI Agent Move Analysis (Algorithm: {algorithm_name})")
        print(f"Search Depth K: {self.K}")
        print(f"Time Taken: {end_time - start_time:.4f} seconds")
        print(f"Nodes Expanded: {nodes_expanded}")
        print(f"Optimal Column Choice: {col}")
        print(f"Evaluated Score: {score}")
        print("="*50)

        return col