import json
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates/")

file_path = "optimal_moves.json"
stats_path = "game_stats.json"

with open(file_path, "r") as f:
    stringified_moves = json.load(f)
    optimal_moves = {eval(key): value for key, value in stringified_moves.items()}

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
        return -1
    return 0

def get_pos(num_turn):
    c = 0
    for i in range(3):
        for j in range(3):
            c += 1
            if int(num_turn) == c:
                return i, j
    return None

def reset_game():
    return [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [['', '', ''], ['', '', ''], ['', '', '']], 9

def load_stats():
    try:
        with open(stats_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"win": 0, "loss": 0, "draw": 0}

def save_stats(stats):
    with open(stats_path, "w") as f:
        json.dump(stats, f)

def get_winning_cells(board, player):
    winning_cells = []
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] == player:
            winning_cells = [(i, 0), (i, 1), (i, 2)]
            break
        if board[0][i] == board[1][i] == board[2][i] == player:
            winning_cells = [(0, i), (1, i), (2, i)]
            break
    if board[0][0] == board[1][1] == board[2][2] == player:
        winning_cells = [(0, 0), (1, 1), (2, 2)]
    elif board[0][2] == board[1][1] == board[2][0] == player:
        winning_cells = [(0, 2), (1, 1), (2, 0)]
    
    return winning_cells

sol, board, moves = reset_game()
symbols = {1: "X", 2: "O"}
stats = load_stats()

@app.route('/')
def index():
    global sol, board, moves
    sol, board, moves = reset_game()
    return render_template('index.html', board=board, stats=stats)


@app.route('/make_move', methods=['POST'])
def make_move():
    global sol, board, stats
    user_move = int(request.form.get('move')) + 1
    pos = get_pos(user_move)

    if pos is None or sol[pos[0]][pos[1]] != 0:
        return jsonify({"winner": None, "board": board})
    
    sol[pos[0]][pos[1]] = 2
    board[pos[0]][pos[1]] = symbols[2]

    winner = check_winner(sol)
    if winner == 2:
        stats["win"] += 1
        save_stats(stats)
        return jsonify({
            "winner": "You (O) win!",
            "board": board,
            "winning_cells": get_winning_cells(sol, 2)
        })

    flattened_board = tuple(sum(sol, []))
    possible_moves = [i + 1 for i, v in enumerate(flattened_board) if v == 0]
    if not possible_moves:
        stats["draw"] += 1
        save_stats(stats)
        return jsonify({
            "winner": "It's a draw!",
            "board": board,
        })

    move = optimal_moves.get(flattened_board, random.choice(possible_moves))
    ai_pos = get_pos(move)
    sol[ai_pos[0]][ai_pos[1]] = 1
    board[ai_pos[0]][ai_pos[1]] = symbols[1]

    winner = check_winner(sol)
    if winner == 1:
        stats["loss"] += 1
        save_stats(stats)
        return jsonify({
            "winner": "AI (X) wins!",
            "board": board,
            "winning_cells": get_winning_cells(sol, 1)
        })
    elif winner == -1:
        stats["draw"] += 1
        save_stats(stats)
        return jsonify({
            "winner": "It's a draw!",
            "board": board,
        })
    else:
        return jsonify({
            "winner": None,
            "board": board,
        })
        
        
@app.route('/start_game', methods=['GET'])
def start_game():
    global sol, board, stats
    sol, board, moves = reset_game()
    
    move = random.randint(1, 9)
    
    ai_pos = get_pos(move)
    sol[ai_pos[0]][ai_pos[1]] = 1
    board[ai_pos[0]][ai_pos[1]] = symbols[1]
    return jsonify({
        "board": board
    })

@app.route('/restart', methods=['POST'])
def restart():
    global sol, board, moves
    sol, board, moves = reset_game()
    return render_template('index.html', board=board, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
