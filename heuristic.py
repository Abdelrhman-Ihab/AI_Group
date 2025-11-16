import numpy as np


rows,cols = (6,7)



def heuristic(arr,player):
    one_radius_score = 0
    two_radius_score = 0
    for i in range(rows):
        for j in range(cols):
            if arr[i][j] == player :#my piece is here
                one_radius_score += one_radius(arr,i,j,player)#returns score of one radius
                two_radius_score += two_radius(arr,i,j,player)#returns score of two radius
                #no need for 3 radius as thats end winning state
    return one_radius_score + two_radius_score# can multiple two_radius_score by some value


def bound_check(arr,i,j,player):
    if i<0 or j<0:
        return 0
    if i==rows or j==cols:
        return 0
    if arr[i][j] == player:#my piece
        return 1
    else:
        return 0

def one_radius(arr,i,j,player):
    count = 0
    spaces = [[0,1],[1,1],[1,0],[1,-1]]#right right_down down left_down
    for space in spaces:
        if bound_check(arr,i+space[0],j+space[1],player):
            count+= 1
    return count
        
def two_radius(arr,i,j,player):
    count = 0
    spaces = [[0,1],[1,1],[1,0],[1,-1]]
    #spaces = [[[0,1],[0,2]],[[1,1],[2,2]],[[1,0],[2,0]],[[0,-1],[0,-2]]]
    for space in spaces:
        if bound_check(arr,i+space[0],j+space[1],player) and bound_check(arr,i+2*space[0],j+2*space[1],player):
            count+=1
    return count

#can combine one_radius and two_radius into one function


temp = [[0]*cols]*rows

arr = np.zeros((rows,cols))
arr[0][0] = 1
arr[0][1] = 1
arr[0][2] = 1 
arr[0][3] = 1
arr[1][2] = 1
print(arr)
print(heuristic(arr,1))
