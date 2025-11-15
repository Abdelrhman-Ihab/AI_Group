import random
import numpy as np

class AI_Agent:
    def __init__(self):
        pass
    def make_move(self, state : np.array):
        valid_cols = [c for c in range(state.shape[1]) if state[0, c] == 0]
        if not valid_cols:
            return None
        col = random.choice(valid_cols)
        return col