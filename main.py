import json
import random
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__, template_folder="templates/")

# Path to the file
file_path = "optimal_moves.json"

# Load the data and convert string keys back to tuples
with open(file_path, "r") as f:
    stringified_moves = json.load(f)
    optimal_moves = {eval(key): value for key, value in stringified_moves.items()}

# Check for the winner
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

# Get position from input [1..9]
def get_pos(num_turn):
    c = 0
    for i in range(3):
        for j in range(3):
            c += 1
            if int(num_turn) == c:
                return i, j
    return None

# Initialize game state
def reset_game():
    return [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [['', '', ''], ['', '', ''], ['', '', '']], 9

sol, board, moves = reset_game()  # Initial game state

symbols = {1: "X", 2: "O"}

def ai_start_first():
    rand_row = random.randint(0, 2)
    rand_col = random.randint(0, 2)
    sol[rand_row][rand_col] = 1
    board[rand_row][rand_col] = "X"

@app.route('/')
def index():
    return render_template('index.html', board=board)

@app.route('/make_move', methods=['POST'])
def make_move():
    global sol, board, moves
    moves -= 2
    user_move = int(request.form.get('move'))  # User's move (O)

    # User's turn (O)
    pos = get_pos(user_move)
    sol[pos[0]][pos[1]] = 2
    board[pos[0]][pos[1]] = symbols[2]
    
    # Check for a winner after the user's move
    winner = check_winner(sol)
    if winner == 2:
        return jsonify({
            "winner": "You (O) win!", 
            "board": board, 
            "disable_buttons": True,
            "winning_cells": get_winning_cells(sol, 2)
        })

    # AI's turn (X)
    flattened_board = tuple(sum(sol, []))  # Flatten board to match dataset
    move = optimal_moves.get(flattened_board, random.choice([i + 1 for i, v in enumerate(flattened_board) if v == 0]))
    
    ai_pos = get_pos(move)
    sol[ai_pos[0]][ai_pos[1]] = 1
    board[ai_pos[0]][ai_pos[1]] = symbols[1]
    
    # Check for a winner after AI's move
    winner = check_winner(sol)
    if winner == 1:
        return jsonify({
            "winner": "AI (X) wins!", 
            "board": board, 
            "disable_buttons": True,
            "winning_cells": get_winning_cells(sol, 1)
        })
    elif winner == -1:
        return jsonify({
            "winner": "It's a draw!", 
            "board": board, 
            "disable_buttons": True
        })
    
    return jsonify({
        "winner": None, 
        "board": board, 
        "disable_buttons": False
    })

def get_winning_cells(board, player):
    """Get the cells of the winning line for a given player."""
    winning_cells = []
    for i in range(3):
        # Check rows
        if board[i][0] == board[i][1] == board[i][2] == player:
            winning_cells = [(i, 0), (i, 1), (i, 2)]
            break
        # Check columns
        if board[0][i] == board[1][i] == board[2][i] == player:
            winning_cells = [(0, i), (1, i), (2, i)]
            break
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == player:
        winning_cells = [(0, 0), (1, 1), (2, 2)]
    elif board[0][2] == board[1][1] == board[2][0] == player:
        winning_cells = [(0, 2), (1, 1), (2, 0)]
    
    return winning_cells

@app.route('/restart', methods=['POST'])
def restart():
    global sol, board, moves
    sol, board, moves = reset_game()  # Reset the game state
    ai_start_first()
    return render_template('index.html', board=board)

if __name__ == '__main__':
    app.run(debug=True)
