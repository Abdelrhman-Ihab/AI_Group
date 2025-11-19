import random
import numpy as np
import random
import time
import math

infinity = math.inf
INF = math.inf
ROWS = 6
COLS = 7
EMPTY = 0
P1_PIECE = 1  # (Human)
P2_PIECE = 2  # (AI)

PROB_CHOSEN = 0.6
PROB_SIDE_AVAILABLE = 0.2
PROB_ONE_SIDE_ONLY = 0.4

# Global counter for nodes expanded in Minimax
nodes_expanded = 0

# bitboard shift constants
SHIFT_H  = ROWS          # horizontal
SHIFT_V  = 1       # vertical
SHIFT_D1 = ROWS + 1   # diag up-right
SHIFT_D2 = ROWS - 1   # diag down-right
CENTER_COLS = [10, 20, 30, 40, 30, 20, 10]

class AI_Agent:
    def __init__(self,depth,algorithm):
        self.algorithm = algorithm
        self.depth = depth
        
    def make_move(self, state : np.array):
        temp = board_to_bits(state)
        board = BitBoard(temp[0],temp[1],temp[2])
       # print(bits_to_board_array(board.mask,board.board1,board.board2))
        #print("")
        if self.algorithm == "Minimax":
            return minimax(board,self.depth,0,0,True,False)[0]
        if self.algorithm == "Alpha-Beta":
            return minimax(board,self.depth,-infinity,infinity,True,True)[0]
        if self.algorithm == "Expected":
            return expected_minimax(board,self.depth,True)[0]
        


def board_to_bits(board):
    mask = 0
    b1 = 0
    b2 = 0
    
    # Column-major: bit index = bitboard_row + col * ROWS
    for col in range(COLS):
        for row in range(ROWS):
            cell = board[row, col]
            
            # --- THE CRITICAL FIX: INVERT THE ROW INDEX ---
            # If row=5 (bottom-most in GUI), bitboard_row = 6 - 1 - 5 = 0 (bottom-most bit)
            # If row=0 (top-most in GUI), bitboard_row = 6 - 1 - 0 = 5 (top-most bit)
            bitboard_row = (ROWS - 1) - row
            
            bit_index = bitboard_row + col * ROWS
            bit = 1 << bit_index

            if cell == 1:
                b1 |= bit
            elif cell == 2:
                b2 |= bit
                
    mask = b1 | b2
    return mask, b1, b2

def bits_to_board_array(mask, board1, board2):
    """
    Converts the BitBoard representation (mask, b1, b2) back into a 6x7 NumPy array.
    This is the inverse check for board_to_bits, crucial for debugging.
    """
    ROWS = 6 
    COLS = 7
    board_array = np.zeros((ROWS, COLS), dtype=int)
    
    for col in range(COLS):
        for bitboard_row in range(ROWS):
            # Calculate the bit index based on BitBoard's column-major order
            bit_index = bitboard_row + col * ROWS
            bit = 1 << bit_index
            
            # 1. Determine the player in the cell
            player = EMPTY
            if (board1 & bit):
                player = P1_PIECE
            elif (board2 & bit):
                player = P2_PIECE
                
            # 2. Convert the BitBoard row back to the GUI's NumPy row index
            # BitBoard row 0 (bottom bit) -> GUI row 5 (bottom row)
            # BitBoard row 5 (top bit)    -> GUI row 0 (top row)
            gui_row = (ROWS - 1) - bitboard_row
            
            # 3. Assign to the array
            board_array[gui_row, col] = player
            
    return board_array

# Global counter for nodes expanded in Minimax
nodes_expanded = 0

class BitBoard:
    def __init__(self,mask=0,board1=0,board2=0):
        self.mask = mask      # all occupied cells
        self.board1 = board1
        self.board2 = board2

    def copy(self):
        c = BitBoard()
        c.mask = self.mask
        c.board1 = self.board1
        c.board2 = self.board2
        return c

    # make_move as before
    def make_move(self, col, player):
        col_mask = ((1 << ROWS) - 1) << (col * ROWS)
        filled = self.mask & col_mask
        next_cell = ((filled + (1 << (col * ROWS))) ^ filled) & col_mask
        self.mask |= next_cell
        if player == 1:
            self.board1 |= next_cell
        else:
            self.board2 |= next_cell

    # --------- Correct counting with open-end check ---------
    def count_twos_threes_fours(self):
        b1 = self.board1
        b2 = self.board2
        FULL_MASK = (1 << (ROWS * COLS)) - 1

        # Masks to prevent wrapping
        NO_RIGHT = FULL_MASK
        for col in range(COLS-1, COLS):
            NO_RIGHT &= ~(((1 << ROWS) - 1) << (col * ROWS))
        NO_LEFT = FULL_MASK
        for col in range(0, 1):
            NO_LEFT &= ~(((1 << ROWS) - 1) << (col * ROWS))

        p1_twos = p1_threes = p1_fours = 0
        p2_twos = p2_threes = p2_fours = 0

        directions = [(SHIFT_H, NO_RIGHT, NO_RIGHT),  # horiz
                      (SHIFT_V, FULL_MASK, FULL_MASK), # vertical
                      (SHIFT_D1, NO_RIGHT, NO_RIGHT),  # diag up-right
                      (SHIFT_D2, NO_RIGHT, NO_RIGHT)]  # diag down-right

        for shift, mask, mask_end in directions:
            # Player 1
            s1 = (b1 & mask) >> shift
            s2 = s1 >> shift
            s3 = s2 >> shift
            s4 = s3 >> shift  # the 4th cell for open-end check

            # Only count sequences that can extend to 4 (open-end)
            open_end = ~(b1 | b2)  # empty cells
            p1_2 = b1 & s1 & (s2 | (open_end >> (2*shift)))
            p1_3 = b1 & s1 & s2 & (s3 | (open_end >> (3*shift)))
            p1_4 = b1 & s1 & s2 & s3

            p1_twos   += p1_2.bit_count()
            p1_threes += p1_3.bit_count()
            p1_fours  += p1_4.bit_count()

            # Player 2
            s1 = (b2 & mask) >> shift
            s2 = s1 >> shift
            s3 = s2 >> shift
            s4 = s3 >> shift

            open_end = ~(b1 | b2)
            p2_2 = b2 & s1 & (s2 | (open_end >> (2*shift)))
            p2_3 = b2 & s1 & s2 & (s3 | (open_end >> (3*shift)))
            p2_4 = b2 & s1 & s2 & s3

            p2_twos   += p2_2.bit_count()
            p2_threes += p2_3.bit_count()
            p2_fours  += p2_4.bit_count()

        return (p1_twos, p1_threes, p1_fours,
                p2_twos, p2_threes, p2_fours)



    # ------- HEURISTIC SCORE -------
    def heuristic(self, piece, C2=10, C3=50, C4=10000):
        # Count sequences from board
        p1_twos, p1_threes, p1_fours, p2_twos, p2_threes, p2_fours = self.count_twos_threes_fours()

        # Assign my/opp based on who is evaluating
        if piece == P1_PIECE:
            my_twos, my_threes, my_fours = p1_twos, p1_threes, p1_fours
            opp_twos, opp_threes, opp_fours = p2_twos, p2_threes, p2_fours
            my_board = self.board1
            opp_board = self.board2
        else:
            my_twos, my_threes, my_fours = p2_twos, p2_threes, p2_fours
            opp_twos, opp_threes, opp_fours = p1_twos, p1_threes, p1_fours
            my_board = self.board2
            opp_board = self.board1

        # Center column bonus (column-major bitboard)
        center_score = 0
        for col in range(COLS):
            col_mask = ((1 << ROWS) - 1) << (col * ROWS)
            center_score += CENTER_COLS[col] * (
                my_board & col_mask
            ).bit_count()
            center_score -= CENTER_COLS[col] * (
                opp_board & col_mask
            ).bit_count()

        # Final score
        return (
            C2 * (my_twos - opp_twos)
            + C3 * (my_threes - opp_threes)
            + C4 * (my_fours - opp_fours)
            + center_score
        )



    # ----------- POSSIBLE MOVES (same as before) ------------
    def possible_moves(self):
        moves = []
        for col in range(COLS):
            top_bit = col * ROWS + (ROWS - 1)
            if not (self.mask & (1 << top_bit)):
                moves.append(col)
        return moves
    
    def is_terminal_node(self):
        # Terminal when the board is full
        # mask has 1s in all occupied cells
        FULL_MASK = (1 << (ROWS * COLS)) - 1
        return self.mask == FULL_MASK

        

def minimax(
    board_object, depth, alpha, beta, maximizing_player, use_alpha_beta
):
    global nodes_expanded
    nodes_expanded += 1

    is_board_full = board_object.is_terminal_node()
    if depth == 0 or is_board_full:
        return (None, board_object.heuristic(P2_PIECE))

    valid_moves = board_object.possible_moves()
    best_col = random.choice(valid_moves)#could be slow
    if maximizing_player:
        value = -INF
        for col in valid_moves:
            temp_board_obj = board_object.copy()
            temp_board_obj.make_move(col,P2_PIECE)
            new_score = minimax(
                temp_board_obj,
                depth - 1,
                alpha,
                beta,
                False,
                use_alpha_beta,
            )[1]

            if new_score > value:
                value = new_score
                best_col = col

            if use_alpha_beta:
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        print("value",value)
        return best_col, value
    else:
        value = INF
        for col in valid_moves:
            temp_board_obj = board_object.copy()
            temp_board_obj.make_move(col,P1_PIECE)
            new_score = minimax(
                temp_board_obj,
                depth - 1,
                alpha,
                beta,
                True,
                use_alpha_beta,
            )[1]

            if new_score < value:
                value = new_score
                best_col = col

            if use_alpha_beta:
                beta = min(beta, value)
                if alpha >= beta:
                    break
        return best_col, value


def chance_node(
    board_object, chosen_col, depth, next_is_max, current_max_player
):

    global nodes_expanded
    nodes_expanded += 1
    total_expected_value = 0
    outcomes = []

    left_col, right_col = chosen_col - 1, chosen_col + 1
    moves = board_object.possible_moves()
    is_left_available = left_col >= 0 and left_col in moves
    is_right_available = right_col < COLS and right_col in moves

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
        if col in moves:
            temp_board_obj = board_object.copy()
            # Decide which piece to drop
            piece = P2_PIECE if current_max_player else P1_PIECE
            temp_board_obj.make_move(col,piece)

            # Recursively calculate expected minimax for next turn
            score_of_outcome = expected_minimax(
                temp_board_obj, depth - 1, next_is_max
            )[1]
            total_expected_value += score_of_outcome * prob

    return total_expected_value


def expected_minimax(board_object, depth, maximizing_player):
    global nodes_expanded
    nodes_expanded += 1

    if depth == 0 or board_object.is_terminal_node():
        return (None, board_object.heuristic(board_object, P2_PIECE))

    valid_moves = board_object.possible_moves()
    best_col = random.choice(valid_moves)

    if maximizing_player:
        value = -INF
        for col in valid_moves:
            expected_score = chance_node(
                board_object, col, depth, False, maximizing_player
            )
            if expected_score > value:
                value = expected_score
                best_col = col
        return best_col, value
    else:
        value = INF
        for col in valid_moves:
            expected_score = chance_node(
                board_object, col, depth, True, maximizing_player
            )
            if expected_score < value:
                value = expected_score
                best_col = col
        return best_col, value

""""
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
            col, score = minimax(
                board_obj, self.K, -INF, INF, True, self.heuristic_func, False
            )
            algorithm_name = "Minimax (No Alpha-Beta)"
        elif self.algorithm_choice == 2:
            col, score = minimax(
                board_obj, self.K, -INF, INF, True, self.heuristic_func, True
            )
            algorithm_name = "Minimax (With Alpha-Beta)"
        elif self.algorithm_choice == 3:
            col, score = expected_minimax(board_obj, self.K, True, self.heuristic_func)
            algorithm_name = "Expected Minimax"
        else:
            return None

        end_time = time.time()

        # Output trace information to the console
        print("\n" + "=" * 50)
        print(f"AI Agent Move Analysis (Algorithm: {algorithm_name})")
        print(f"Search Depth K: {self.K}")
        print(f"Time Taken: {end_time - start_time:.4f} seconds")
        print(f"Nodes Expanded: {nodes_expanded}")
        print(f"Optimal Column Choice: {col}")
        print(f"Evaluated Score: {score}")
        print("=" * 50)

        return col
"""