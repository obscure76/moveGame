import os, sys, signal, getopt
import random


#
# Python 3
#

class Move:
    def __init__(self, player_index, row, col):
        self.player_index = player_index
        self.row = row
        self.col = col


def winning_player_index(board, last_move):
    """
    This function is called after every move, which means that if it is being
    called, a win has not previously been detected.

    :param board: 2-dimensional array of integers containing player indexes
    :param last_move: Move object representing the last move made
    :return: player_index of winner; or -1 if no winner detected
    """
    # radially check from the last move if there are 4 consecutive
    did_win = any(
        is_winner(board, last_move.row, last_move.col, x, y, last_move.player_index)
        for (x, y) in [
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
        ]
    )

    return last_move.player_index if did_win else -1


def is_winner(board, x, y, x_direction, y_direction, player_index, consecutive_needed=4):
    """
    For a given board, move, and slope, check how many consecutive spaces there are that match player_index

    :param board:
    :param x:
    :param y:
    :param x_direction:
    :param y_direction:
    :param player_index:
    :param consecutive_needed:
    :return:
    """
    max_iterations = consecutive_needed - 1

    consecutive_in_given_direction = consecutive_in_direction(
        board,
        x + x_direction,
        y + y_direction,
        x_direction,
        y_direction,
        player_index,
        max_iterations=max_iterations)

    consecutive_in_opposite_direction = consecutive_in_direction(
        board,
        x + x_direction * -1,
        y + y_direction * -1,
        x_direction * -1,
        y_direction * -1,
        player_index,
        max_iterations=max_iterations)

    max_consecutive = 1 + consecutive_in_given_direction + consecutive_in_opposite_direction

    return max_consecutive >= consecutive_needed


def consecutive_in_direction(board, x, y, x_direction, y_direction, player_index, current_iteration=1,
                             max_iterations=3):
    if current_iteration > max_iterations:
        return 0
    if not (0 <= x < len(board)):
        return 0
    if not (0 <= y < len(board[0])):
        return 0
    if board[x][y] == player_index:
        next_x = x + x_direction
        next_y = y + y_direction
        return 1 + consecutive_in_direction(board, next_x, next_y, x_direction, y_direction, player_index,
                                            current_iteration + 1, max_iterations)
    return 0


##### COMMAND-LINE ARGS #####

ROWS = 6
COLS = 7
HUMANS = 2
ROBOTS = 0

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["rows=", "cols=", "humans=", "robots="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    sys.exit(2)

for o, a in opts:
    if o in ("--rows"):
        assert a.isdigit(), a + ' is not a valid option for rows.'
        ROWS = int(a)
    elif o in ("--cols"):
        assert a.isdigit(), a + ' is not a valid option for cols.'
        COLS = int(a)
    elif o in ("--humans"):
        assert a.isdigit(), a + ' is not a valid option for humans.'
        HUMANS = int(a)
    elif o in ("--robots"):
        assert a.isdigit(), a + ' is not a valid option for robots.'
        ROBOTS = int(a)
    else:
        assert False, "Unhandled option:  " + o

print('\n>>>>> Board = {} rows x {} cols; Human Players = {}; Robot Players = {}'.format(ROWS, COLS, HUMANS, ROBOTS))
PLAYERS = HUMANS + ROBOTS

print(PLAYERS)
if PLAYERS > 2:
    raise Exception("Only 2 players can play")


##### PREDEFINED FUNCTIONS #####

def is_valid_move(board, move):
    """
    Checks if move is valid
    :param board: 2-dimensional array of integers containing player indexes
    :param move: Move object representing the move to validate
    :return: boolean if move is valid given board
    """

    # check min boundary violations
    if move.row < 0 or move.col < 0:
        return False

    # check max boundary violations
    if move.row >= len(board) or move.col >= len(board[0]):
        return False

    # can't place over existing piece
    if board[move.row][move.col] > -1:
        return False

    # check that we are stacking if not on bottom row
    if move.row < len(board) - 1 and board[move.row + 1][move.col] < 0:
        return False

    return True


def update_board(board, move):
    """
    Update board with move.
    :param board: 2-dimensional array of integers containing player indexes
    :param move: Move object representing the move to update on board
    :return:
    """
    board[move.row][move.col] = move.player_index


def parse_move(player_index, move_input):
    token = move_input.strip()
    if not token.isdigit():
        return None
    col = int(token) - 1
    row = find_row(col)
    print("row = {}, col = {}".format(row, col))
    if row is None:
        return None
    move = Move(player_index, row, col)
    print('Player #{} places piece in row = {}, col = {}.'.format(player_index + 1, row + 1, col + 1));
    return move


def find_row(col):
    for i in range(ROWS - 1, -1, -1):
        if board[i][col] == -1:
            return i
    return None


def exit_script():
    print('\n\nExiting...\n\n')
    sys.exit(0)


def sigint_handler(signal, frame):
    exit_script()


def prompt_str_val(prompt):
    print
    while (True):
        choice = input(prompt)
        choice = choice.strip()
        if (len(choice) > 0):
            return choice


def print_board(board, player_symbols):
    print()
    print('    ', end='')
    for col_index in range(len(board[0])):
        print("{:>3} ".format(col_index + 1), end='')
    print()
    for row_index in range(len(board)):
        row = board[row_index]
        print("{:>3} ".format(row_index + 1), end='')
        for col in range(len(row)):
            player_symbol = '.'
            player_index = board[row_index][col]
            if player_index >= 0:
                player_symbol = player_symbols[player_index]
            print("{:>3} ".format(player_symbol), end='')
        print()
    print()


def open_spots():
    res = 0
    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r][c] == -1:
                res += 1
    return res


def get_robot_move():
    count = 0
    move = None
    while open_spots():
        move_input = str(count)
        count += 1
        move = parse_move(player_index, move_input)
        if move is not None and is_valid_move(board, move):
            break
    return move


def get_human_move():
    move_input = prompt_str_val("Player #{} Move [ col ]:  ".format(display_player_id))
    return parse_move(player_index, move_input)


##### MAIN #####

# catch ctrl-c
signal.signal(signal.SIGINT, sigint_handler)

# map player_index to a symbol so board is easier to view
PLAYER_SYMBOLS = ['X', 'O', 'A', 'B', 'C', 'D', 'E', 'Y', 'Z', 'H']

# initialize board
board = [[-1 for cols in range(COLS)] for rows in range(ROWS)]

# main terminal interface loop
move_count = 0
while True:
    for player_index in range(PLAYERS):
        display_player_id = player_index + 1
        print_board(board, PLAYER_SYMBOLS)

        while True:
            if ROBOTS == 2:
                move = get_robot_move()
            elif ROBOTS == 1:
                if display_player_id == 2:
                    move = get_robot_move()
                else:
                    move = get_human_move()
            else:
                move = get_human_move()
                print(move)
            if move is not None and is_valid_move(board, move):
                update_board(board, move)
                move_count += 1
                break
            else:
                print("INVALID MOVE", move)

        if winning_player_index(board, move) > -1:
            print_board(board, PLAYER_SYMBOLS)
            print('\n\nPlayer #{} wins!\n\n'.format(display_player_id))
            exit_script()

        if move_count == (ROWS * COLS):
            print_board(board, PLAYER_SYMBOLS)
            print("\n\nIt's a draw!")
            exit_script()
