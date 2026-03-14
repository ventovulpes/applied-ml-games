import random
from tic_tac_toe_tree import TicTacToeTree
from heuristic_tic_tac_toe_tree import HeuristicTicTacToeTree

class Player:
    strategy_function = None

    def __init__(self, strategy_function):
        self.strategy_function = strategy_function

    def choose_move(self, board) -> int:
        return self.strategy_function(board)
    
class MinimaxPlayer:
    def __init__(self, player_perspective: int):
        self.tree = TicTacToeTree(player_perspective)
    
    def choose_move(self, board) -> int:
        node = self.tree.nodes[self.tree.hash_state(board.board)]
        children = self.tree.get_children(node)
        if not children:
            return
        max = children[0].minimax
        best_choices = [children[0]]
        for c in children:
            if c.minimax > max:
                max = c.minimax
                best_choices.clear()
                best_choices.append(c)
            elif c.minimax == max:
                best_choices.append(c)
        return self.tree.get_move_change(node.state, best_choices[random.randint(0, len(best_choices) - 1)].state)
    
class HeuristicMinimaxPlayer:
    def __init__(self, player_perspective: int, n_ply):
        self.tree = HeuristicTicTacToeTree(player_perspective, n_ply)
    
    def choose_move(self, board) -> int:
        node = self.tree.nodes[self.tree.hash_state(board.board)]
        self.tree.update_tree(node.state)
        children = self.tree.get_children(node)
        if not children:
            return
        max = children[0].minimax
        best_choices = [children[0]]
        for c in children:
            if c.minimax > max:
                max = c.minimax
                best_choices.clear()
                best_choices.append(c)
            elif c.minimax == max:
                best_choices.append(c)
        return self.tree.get_move_change(node.state, best_choices[random.randint(0, len(best_choices) - 1)].state)

class Board:
    board = None
    
    def __init__(self, prev_board = None, move_pos: int = None, symbol: str = None):
        if not prev_board:
            self.board = [
                [None, None, None],
                [None, None, None],
                [None, None, None]
            ]
            return
        
        if not move_pos and not symbol:
            self.board = self.copy_board(prev_board)
            return
        
        if not prev_board.is_valid_move(move_pos):
            print('invalid move')
            return
        
        self.board = self.copy_board(prev_board)
        move_coords = self.position_to_coords(move_pos)
        self.board[move_coords[0]][move_coords[1]] = symbol

    def copy_board(self, board):
        new_board = []
        for r in range(len(board.board)):
            new_board.append([])
            for c in board.board[r]:
                new_board[r].append(c)
        return new_board

    def position_to_coords(self, pos: int) -> tuple[int, int]:
        if not 0 <= pos <= 8:
            raise ValueError(f'position {pos} is invalid')
        return (int(pos / 3), pos % 3)

    def get_player_at_position(self, pos: int) -> str:
        coords = self.position_to_coords(pos)
        return self.board[coords[0]][coords[1]]
    
    def is_valid_move(self, pos: int) -> bool:
        return self.get_player_at_position(pos) == None
    
    def is_filled(self) -> bool:
        is_filled = True
        for r in self.board:
            for c in r:
                if not c:
                    is_filled = False
        return is_filled
    
    def get_winner(self) -> str:
        for row in self.board:
            symbol = row[0]
            if not symbol:
                continue
            won_by_row = True
            for n in row:
                if n != symbol:
                    won_by_row = False
                    break
            if won_by_row:
                return symbol
        for c in range(3):
            symbol = self.board[0][c]
            if not symbol:
                continue
            won_by_col = True
            for row in self.board:
                if row[c] != symbol:
                    won_by_col = False
                    break
            if won_by_col:
                return symbol
        top_left = self.board[0][0]
        if top_left:
            if top_left == self.get_player_at_position(4) and top_left == self.get_player_at_position(8):
                return top_left
        top_right = self.board[0][2]
        if top_right:
            if top_right == self.get_player_at_position(4) and top_right == self.get_player_at_position(6):
                return top_right
        return None
     
    def show(self):
        print('-------------')
        for r in self.board:
            a = r[0] if r[0] else " "
            b = r[1] if r[1] else " "
            c = r[2] if r[2] else " "
            print(f'| {a} | {b} | {c} |')
            print('-------------')
        print()
    
class Game:
    board = Board()
    p1 = None
    p2 = None
    game_over = False
    p1_turn = True

    def __init__(self, p1: Player, p2: Player):
        self.board = Board()
        self.p1 = p1
        self.p2 = p2

    def run(self, log: bool = False):
        game_over = False
        while not self.board.is_filled() and not game_over:
            if log:
                self.board.show()

            valid_move = False
            while not valid_move:
                if self.p1_turn:
                    move = self.p1.choose_move(Board(self.board))
                    symbol = 'X'
                else:
                    move = self.p2.choose_move(Board(self.board))
                    symbol = 'O'
                
                if self.board.is_valid_move(move):
                    self.board = Board(self.board, move, symbol)
                    valid_move = True
                    if log:
                        print(f'{'Player X:' if self.p1_turn else 'Player O:'} {self.board.position_to_coords(move)}')
                else:
                    print('Invalid move. Try again.')
            
            self.p1_turn = not self.p1_turn
            if self.board.get_winner():
                game_over = True
        self.board.show()
        if self.board.get_winner():
            print(f'{self.board.get_winner()} Wins')
            return self.board.get_winner()
        else:
            print('Tie Game')
            return None

def random_strategy_function(board,):
    while True:
        try_position = random.randint(0, 8)
        if board.is_valid_move(try_position):
            return try_position
        
def manual_strategy_function(board):
    while True:
        user_input = input('Input position (0-8): ')
        try:
            try_position = int(user_input)
        except ValueError:
            print('Invalid input. Must be an integer. Try again.')
            continue
        if not 0 <= try_position <= 8:
            print('Invalid input. Must be between 0-8. Try again.')
            continue
        if board.is_valid_move(try_position):
            return try_position
        elif try_position:
            print('Invalid move. Try again.')

def cheater_strategy_function(board):
    for i in range(3):
        for j in range(3):
            board.board[i][j] = 'X'
    return 0

def in_order_strategy_function(board):
    for i in range(9):
        if board.is_valid_move(i):
            return i
        else:
            continue

# TESTING MINIMAX VS RANDOM

# num_wins = 0
# num_ties = 0
# total_games = 0
# minimax_first = True
# ms = [MinimaxPlayer(0), MinimaxPlayer(1)]
# for i in range(100):
#     if minimax_first:
#         g = Game(MinimaxPlayer(0), Player(random_strategy_function))
#         winner = g.run(False)
#         if winner == 'X':
#             num_wins += 1
#         elif winner is None:
#             num_ties += 1
#     else:
#         g = Game(Player(random_strategy_function), MinimaxPlayer(1))
#         winner = g.run(False)
#         if winner == 'O':
#             num_wins += 1
#         elif winner is None:
#             num_ties += 1
#     total_games += 1
#     minimax_first = not minimax_first
# print(f'({num_wins} wins + {num_ties} ties) = {num_wins + num_ties} / {total_games} for minimax 1')

g = Game(Player(manual_strategy_function), MinimaxPlayer(1))
g.run(True)