import random
import time
import numpy as np

rows,cols = (6,7)


def heuristic(arr,player):
    score_radius_of_player_one = [0,0,0]
    score_radius_of_player_two = [0,0,0]
    for i in range(rows):
        for j in range(cols):
            if arr[i][j] == 1 :#my piece is here
                temp_window = radius_window(arr,i,j,1)
                for k in range(3):
                    score_radius_of_player_one[k] += temp_window[k]
            elif arr[i][j] == 2:
                temp_window = radius_window(arr,i,j,2)
                for k in range(3):
                    score_radius_of_player_two[k] += temp_window[k]
    reward_constants = [20,400,10000]# one_radius , two_radius, three_radius 
    score = 0
    for i in range(3):
        score+= reward_constants[i] * (score_radius_of_player_one[i]- score_radius_of_player_two[i])
    if player == 1:
        return score
    elif player == 2:
        return -score
    
    


def bound_check(arr,i,j,player):
    if i<0 or j<0:
        return 0
    if i==rows or j==cols:
        return 0
    if arr[i][j] == player:#my piece
        return 1
    else:
        return 0

def radius_window(arr,i,j,player):
    count= [0,0,0]
    spaces = [[0,1],[1,1],[1,0],[1,-1]]#right right_down down left_down
    for space in spaces:
        if bound_check(arr,i+space[0],j+space[1],player):
            count[0]+= 1
            if bound_check(arr,i+2*space[0],j+2*space[1],player):
                count[1]+= 1
                if bound_check(arr,i+3*space[0],j+3*space[1],player):
                    count[2]+=1
    return count

board = np.zeros((rows, cols), dtype=np.int8)


runs = 823543

boards = [np.random.randint(0, 3, size=(rows, cols), dtype=np.int8)
          for _ in range(runs)]

start = time.time()

for board in boards:
    heuristic(board,1)

end = time.time()

print("Total time:", end - start, "seconds")
print("Average per board:", (end - start) / runs, "seconds")

