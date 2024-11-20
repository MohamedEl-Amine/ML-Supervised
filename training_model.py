from itertools import product
import json
import os
import random
def check_winner(sol):
    for i in range(3):
        if sol[i][0] == sol[i][1] == sol[i][2] != 0:
            return sol[i][0]
        if sol[0][i] == sol[1][i] == sol[2][i] != 0:
            return sol[0][i]
    if sol[0][0] == sol[1][1] == sol[2][2] != 0:
        return sol[0][0]
    if sol[0][2] == sol[1][1] == sol[2][0] != 0:
        return sol[0][2]
    if all(sol[i][j] != 0 for i in range(3) for j in range(3)):
        return -1  # Draw
    return 0

def minimax(sol, is_maximizing):
    winner = check_winner(sol)
    if winner == 1:
        return 10  # AI wins
    elif winner == 2:
        return -10  # Player wins
    elif winner == -1:
        return 0  # Draw

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if sol[i][j] == 0:  # Empty cell
                    sol[i][j] = 1  # AI move
                    score = minimax(sol, False)
                    sol[i][j] = 0
                    best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if sol[i][j] == 0:  # Empty cell
                    sol[i][j] = 2  # Player move
                    score = minimax(sol, True)
                    sol[i][j] = 0
                    best_score = min(best_score, score)
        return best_score

def best_move(sol):
    best_score = -float('inf')
    move = None
    for i in range(3):
        for j in range(3):
            if sol[i][j] == 0:  # Empty cell
                sol[i][j] = 1  # AI move
                score = minimax(sol, False)
                sol[i][j] = 0
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

def flatten_board(sol):
    return tuple(sum(sol, []))  # Convert 2D board to a single tuple

# Generate all possible board states
def generate_all_states():
    states = []
    for state in product([0, 1, 2], repeat=9):  # 3^9 states
        board = [list(state[i:i + 3]) for i in range(0, 9, 3)]  # Convert flat to 2D
        if is_valid_board(board):
            states.append(board)
    return states

def is_valid_board(sol):
    # Check if the board state is valid (number of Xs and Os is balanced or off by one)
    x_count = sum(row.count(1) for row in sol)
    o_count = sum(row.count(2) for row in sol)
    return x_count == o_count or x_count == o_count + 1

# Create optimal moves
optimal_moves = {}
all_states = generate_all_states()

for state in all_states:
    if check_winner(state) == 0:  # Only calculate moves for unfinished games
        move = best_move(state)
        if move:
            row, col = move
            pos = row * 3 + col + 1  # Convert (i, j) to position [1..9]
            optimal_moves[flatten_board(state)] = pos

# Convert tuple keys to strings for JSON compatibility
stringified_moves = {str(key): value for key, value in optimal_moves.items()}

# Create or open the file to ensure it exists
file_path = "./optimal_moves.json"
if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        f.write("{}")  # Initialize with an empty JSON object

# Save the optimal_moves dictionary to the file
with open(file_path, "w") as f:
    json.dump(stringified_moves, f)

